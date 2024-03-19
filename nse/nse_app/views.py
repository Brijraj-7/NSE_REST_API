from rest_framework import viewsets
from .models import Index, IndexPrice
from .serializers import IndexSerializer, IndexPriceSerializer
from rest_framework.decorators import api_view
from django.shortcuts import render
from rest_framework.views import APIView
import csv, io
from datetime import datetime
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser


# all index and indexprice 
class IndexViewSet(viewsets.ModelViewSet):
    queryset = Index.objects.all()
    serializer_class = IndexSerializer

class IndexPriceViewSet(viewsets.ModelViewSet):
    queryset = IndexPrice.objects.all()
    serializer_class = IndexPriceSerializer

class IndexesIndexView(APIView):
    parser_classes = (MultiPartParser, FormParser,)

    def get_object(self, pk):
        try:
            return Index.objects.get(pk=pk)
        except Index.DoesNotExist:
            return Response({'message': 'indexes not found'}, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, pk=None, *args, **kwargs):
        if pk:
            index = self.get_object(pk)
            if index:
                index_serializer = IndexSerializer(index)

                # Filter
                index_prices = IndexPrice.objects.filter(index_id=pk)

                open_value = request.query_params.get('open', None)
                if open_value:
                    index_prices = index_prices.filter(open=open_value)

                high_value = request.query_params.get('high', None)
                if high_value:
                    index_prices = index_prices.filter(high=high_value)

                low_value = request.query_params.get('low', None)
                if low_value:
                    index_prices = index_prices.filter(low=low_value)

                close_value = request.query_params.get('close', None)
                if close_value:
                    index_prices = index_prices.filter(close=close_value)

                shares_traded_value = request.query_params.get('shares_traded', None)
                if shares_traded_value:
                    index_prices = index_prices.filter(shares_traded=shares_traded_value)

                turnover_value = request.query_params.get('turnover', None)
                if turnover_value:
                    index_prices = index_prices.filter(turnover=turnover_value)

                # If date parameters are provided, filter by date or date range
                if 'date' in request.query_params or 'start_date' in request.query_params:
                    date = request.query_params.get('date', None)
                    start_date = request.query_params.get('start_date', None)
                    end_date = request.query_params.get('end_date', None)

                    if date:  # Specific date
                        index_prices = index_prices.filter(date=date)
                    elif start_date and end_date:  # Date range
                        index_prices = index_prices.filter(date__range=[start_date, end_date])
                    else:
                        return Response({"error": "Please provide a date or a date range."}, status=status.HTTP_400_BAD_REQUEST)

                index_price_serializer = IndexPriceSerializer(index_prices, many=True)
                response_data = {
                    "index": index_serializer.data,
                    "index_prices": index_price_serializer.data
                }

                return Response(response_data, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Index not found"}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({"error": "Index ID is required for GET request."}, status=status.HTTP_400_BAD_REQUEST)
        
    
    def delete(self, request, pk, *args, **kwargs):
        index = self.get_object(pk)
        index.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# POST CSV File in Database
@api_view(['POST'])
def csvupload(request):
    if 'file' not in request.FILES:
        return Response({'error': 'No file provided.'}, status=status.HTTP_400_BAD_REQUEST)
    
    new_csv_file = request.FILES['file']
    if not new_csv_file.name.endswith('.csv'):
        return Response({'error': 'Please upload a CSV file.'}, status=status.HTTP_400_BAD_REQUEST)
    
    #index name from request
    index_name = request.data.get('index_name', None)
    if not index_name:
        return Response({'error': 'Index name is required.'}, status=status.HTTP_400_BAD_REQUEST)
    
    #Validate index name
    INDEX_NAME_CHOICES = ['NIFTY 50', 'NIFTY 100', 'NIFTY 200', 'NIFTY NEXT 50', 'NIFTY NEXT 50']
    if index_name not in INDEX_NAME_CHOICES:
        return Response({'error': 'Invalid index name.'}, status=status.HTTP_400_BAD_REQUEST)

    index_instance, _ = Index.objects.get_or_create(name=index_name)

    # Process each row of the uploaded CSV
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