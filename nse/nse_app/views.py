from django.http import Http404
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
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q


# all index and indexprice 
class IndexViewSet(viewsets.ModelViewSet):
    queryset = Index.objects.all()
    serializer_class = IndexSerializer

class IndexPriceViewSet(viewsets.ModelViewSet):
    queryset = IndexPrice.objects.all()
    serializer_class = IndexPriceSerializer

#------------------------------------------------------------------------------------------------------------------------

# Create API endpoints for the first five indexes to allow users to retrieve data.
class FristFiveIndexView(APIView):
    pagination_class = PageNumberPagination

    def get(self, request, num):
        index_prices = Index.objects.all()[:num]
        response_data = []
        for index in index_prices:
            row_data = {
                "id" : index.id,
                "index": index.name,
            }
            response_data.append(row_data)
        return Response(response_data, status=status.HTTP_200_OK)
    
#--------------------------------------------------------------------------------------------------------------------------------
# find by index name and date indexes

class IndexesIndexView(APIView):
   def get(self, request, pk, id):
        try:
            indexes = Index.objects.filter(pk=pk)
            index_price = IndexPrice.objects.filter(id=id)
            index_serializer = IndexSerializer(indexes, many=True)
            price_serializer = IndexPriceSerializer(index_price, many=True)
            indexes_name = index_serializer.data
            prices_data = price_serializer.data  
            response_data = []
            for index_name, price_data in zip(indexes_name, prices_data):
                row_data = {
                    "indexes": index_name,
                    "data": price_data,
                }
                response_data.append(row_data)
            return Response(response_data, status=status.HTTP_200_OK)
        except Index.DoesNotExist:
            return Response({"error": "No indexes found for the specified name and indexes date "}, status=status.HTTP_404_NOT_FOUND)

#--------------------------------------------------------------------------------------------------------------------------------
# delete indexes
        
class IndexesDelateView(APIView):
    def get_object(self, pk):
        try:
            return Index.objects.get(pk=pk)
        except Index.DoesNotExist:
            return Response({"error": "Index not found."}, status=status.HTTP_404_NOT_FOUND) 

    def get(self, request, pk, format=None):
        try:
            indexes = self.get_object(pk)
            serializer = IndexSerializer(indexes)
            return Response(serializer.data)
        
        except Index.DoesNotExist:
            return Response({"error": "Index not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, pk, format=None):
        try:
            indexes = self.get_object(pk)
            indexes.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Http404:
            return Response({"error": "Index not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# class indexesDetailView(APIView):
#     def delete(self, resquest, pk):
#         try:
#             indexes = Index.objects.get(pk=pk)
#         except Index.DoesNotExist:
#             return Response({"error": "No indexes found for the specified index"}, status=status.HTTP_404_NOT_FOUND)  
#         indexes.delete()
#         return Response({'message': 'indexes successfully Delete.'}, status=status.HTTP_201_CREATED)

#--------------------------------------------------------------------------------------------------------------------------------
# Support operations specific to each index, including fetching prices for specific dates

class IndexPriceByDateView(APIView):
    def get(self, request, date):
        try:
            prices = IndexPrice.objects.filter(date=date)
            serializer = IndexPriceSerializer(prices, many=True)
            data = serializer.data
            response_data = []
            for price_data in data:
                response_data.append({
                    "IndexData": {
                        "date": date
                    },
                    "pagination": {
                        "page": 1,  
                        "total_pages": 1,  
                        "total_rows": len(data)
                    },
                    "price": price_data
                })
            return Response(response_data, status=status.HTTP_200_OK)
        except IndexPrice.DoesNotExist:
            return Response({"error": "No prices found for the specified date"}, status=status.HTTP_404_NOT_FOUND)
        
#------------------------------------------------------------------------------------------------------------------------------------
#Implement filtering options for each column: OPEN, HIGH, LOW, CLOSE, SHARES TRADED, TURNOVER.
        
class FilterIndexPriceView(APIView):
    def get(self, request, field):
        value = request.query_params.get('value', None)

        if value is None:
            return Response({"error": "Please provide a value parameter"}, status=status.HTTP_400_BAD_REQUEST)

        # filtering
        valid_fields = ['open', 'high', 'low', 'close', 'sharestraded', 'turnover']
        if field not in valid_fields:
            return Response({"error": "Invalid field parameter"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # filter the queryset based on the field parameter
            filtered_prices = IndexPrice.objects.filter(**{field: value})
        except ValueError:
            return Response({"error": "Invalid value parameter"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = IndexPriceSerializer(filtered_prices, many=True)
        return Response(serializer.data)
#----------------------------------------------------------------------------------------------------------------------------------
# Allow users to specify filters in the request payload (e.g., OPEN>2000).
# i am working this APi
class FiltersIndexPriceView(APIView):
    def get(self, request, fields):
        value = request.query_params.get('value', None)
        print(value)

        if value is None:
            return Response({"error": "Please provide a value parameter"}, status=status.HTTP_400_BAD_REQUEST)

        # filtering
        valid_fields = ['open', 'high', 'low', 'close', 'sharestraded', 'turnover']
        if fields not in valid_fields:
            return Response({"error": "Invalid field parameter"}, status=status.HTTP_400_BAD_REQUEST)
        query=Q()
        try:
            for fields in valid_fields:
                condition = IndexPrice.objects.filter(fields)
                if condition.startswith('>'):
                    query &= Q(**{f'{value}__gt': float(condition[1:])})
                elif condition.startswith('<'):
                    query &= Q(**{f'{value}__lt': float(condition[1:])})
                elif condition.startswith('='):
                    query &= Q(**{f'{value}': float(condition[1:])})
                else:
                    return Response({"error": f"Invalid filter format for {value}."}, status=status.HTTP_400_BAD_REQUEST)
                
            filtered_prices = IndexPrice.objects.filter(query)
        except ValueError:
            return Response({"error": "Invalid value parameter"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = IndexPriceSerializer(filtered_prices, many=True)
        return Response(serializer.data)

#----------------------------------------------------------------------------------------------------------------------------------------
# POST CSV File in Database
@api_view(['POST'])
def csvupload(request):
    if 'file' not in request.FILES:
        return Response({'error': 'No file provided.'}, status=status.HTTP_400_BAD_REQUEST)
    
    new_csv_file = request.FILES['file']
    if not new_csv_file.name.endswith('.csv'):
        return Response({'error': 'Please upload a CSV file.'}, status=status.HTTP_400_BAD_REQUEST)
 
    # Create or find the Index instance before processing rows
    index_instance, _ = Index.objects.get_or_create(name=new_csv_file.name)

    # Process each row of the uploaded CSV
    data_set = new_csv_file.read().decode('UTF-8')
    io_string = io.StringIO(data_set)
    reader = csv.reader(io_string, delimiter=',', quotechar="|")
    
    # Skip the header row
    next(reader, None)
    for row in reader:
            if len(row) == 7:
                try:
                    date = str(row[0])
                    open_price = float(row[1])
                    high = float(row[2])
                    low = float(row[3])
                    close = float(row[4])
                    sharestraded = int(row[5]) if row[5] else 0  # Convert empty string to 0
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

    return Response({'message': 'File successfully processed.'}, status=status.HTTP_201_CREATED)