import logging
import csv
import io
from django.http import HttpResponse
import requests
from datetime import datetime
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.authentication import BasicAuthentication,TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from .models import Index, IndexPrice
from .serializers import IndexSerializer, IndexPriceSerializer, UserSerializer
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from nse_app.tasks import send_mails_func

# logger
logger = logging.getLogger(__name__)
logger = logging.getLogger('django')
logger = logging.getLogger('nse_app')
logger = logging.getLogger('django.request')


def some_view(request): 
    logger.debug('Debug message')
    logger.info('Info message')
    logger.warning('Warning message')
    logger.error('An error occurred while processing the request.')
    logger.critical('Critical message')

@authentication_classes([BasicAuthentication,TokenAuthentication,JWTAuthentication])
@permission_classes([IsAuthenticated])
class IndexViewSet(viewsets.ModelViewSet):
    queryset = Index.objects.all()
    serializer_class = IndexSerializer

@authentication_classes([BasicAuthentication,TokenAuthentication,JWTAuthentication])
@permission_classes([IsAuthenticated])
class IndexPriceViewSet(viewsets.ModelViewSet):
    queryset = IndexPrice.objects.all()
    serializer_class = IndexPriceSerializer

def send_mail_all(request):
    send_mails_func.delay("")  
    return HttpResponse("sent")


@permission_classes([IsAuthenticated])
class CustomAuthToken(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)

        if not serializer.is_valid():
            return Response({'status': 403, 'errors': serializer.errors, 'message': 'something went wrong', })

        serializer.save()
        user = User.objects.get(username=serializer.data['username'])
        token_obj, _ = Token.objects.get_or_create(user=user)
        return Response({'status': 200, 'payload': serializer.data, 'token': str(token_obj), 'message': 'your data'})


    
@authentication_classes([BasicAuthentication, TokenAuthentication,JWTAuthentication])
@permission_classes([IsAuthenticated])
class IndexesIndexView(APIView):
    authentication_classes = [BasicAuthentication,TokenAuthentication,JWTAuthentication]
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser,)

    def get_object(self, pk):
        try:
            return Index.objects.get(pk=pk)
        except Index.DoesNotExist:
            return Response({'message': 'indexes not found'}, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, pk=None, *args, **kwargs):
        try:
            if pk:
                index = self.get_object(pk)
                if index:
                    index_serializer = IndexSerializer(index)

                    index_prices = IndexPrice.objects.filter(index_id=pk)

                    filter_params = {
                        'open': 'open',
                        'high': 'high',
                        'low': 'low',
                        'close': 'close',
                        'shares_traded': 'shares_traded',
                        'turnover': 'turnover'
                    }

                    for param, field_name in filter_params.items():
                        param_value = request.query_params.get(param)
                        if param_value:
                            index_prices = index_prices.filter(**{field_name: param_value})

                    if 'date' in request.query_params or 'start_date' in request.query_params:
                        date = request.query_params.get('date', None)
                        start_date = request.query_params.get('start_date', None)
                        end_date = request.query_params.get('end_date', None)

                        if date:
                            index_prices = index_prices.filter(date=date)
                        elif start_date and end_date:
                            index_prices = index_prices.filter(date__range=[start_date, end_date])
                        else:
                            return Response({"error": "Please provide a date or a date range."}, status=status.HTTP_400_BAD_REQUEST)

                    index_price_serializer = IndexPriceSerializer(index_prices, many=True)
                    response_data = {
                        "index": index_serializer.data,
                        "index_prices": index_price_serializer.data
                    }

                    return Response(response_data, status=status.HTTP_200_OK)
        except:
            return Response({"error": "place valid index ID enter."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response({"error": "Index ID is required for GET request."}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, *args, **kwargs):
        index = self.get_object(pk)
        index.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['POST'])
@authentication_classes([BasicAuthentication,TokenAuthentication,JWTAuthentication])
@permission_classes([IsAuthenticated])
def csvupload(request):
    if 'file' not in request.FILES:
        return Response({'error': 'No file provided.'}, status=status.HTTP_400_BAD_REQUEST)
    
    new_csv_file = request.FILES['file']
    if not new_csv_file.name.endswith('.csv'):
        return Response({'error': 'Please upload a CSV file.'}, status=status.HTTP_400_BAD_REQUEST)
    
    index_name = request.data.get('index_name', None)
    if not index_name:
        return Response({'error': 'Index name is required.'}, status=status.HTTP_400_BAD_REQUEST)
    
    INDEX_NAME_CHOICES = ['NIFTY 50', 'NIFTY 100', 'NIFTY 200', 'NIFTY NEXT 50', 'NIFTY NEXT 50']
    if index_name not in INDEX_NAME_CHOICES:
        return Response({'error': 'Invalid index name.'}, status=status.HTTP_400_BAD_REQUEST)

    index_instance, _ = Index.objects.get_or_create(name=index_name)

    try:
        data_set = new_csv_file.read().decode('UTF-8')
        io_string = io.StringIO(data_set)
        reader = csv.reader(io_string, delimiter=',', quotechar="|")
        
        next(reader, None)
        for row in reader:
            if len(row) == 7:
                try:
                    date = datetime.strptime(row[0], '%d-%b-%Y')
                    open_price = float(row[1])
                    high = float(row[2])
                    low = float(row[3])
                    close = float(row[4])
                    sharestraded = int(row[5]) if row[5] else 0
                    turnover = float(row[6]) if row[6] else 0.0 

                    IndexPrice.objects.update_or_create(
                        index=index_instance,
                        date=date,
                        defaults={
                            'open': open_price,
                            'high': high,
                            'low': low,
                            'close': close,
                            'sharestraded': sharestraded,
                            'turnover': turnover,
                        }
                    )
                except ValueError as e:
                    return Response({'error': f'Error processing row: {row}. Error: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'error': f'Error processing CSV file: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)

    return Response({'message': 'File successfully processed.'}, status=status.HTTP_201_CREATED)
