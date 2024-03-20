from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
from .models import Index, IndexPrice
from rest_framework.renderers import JSONRenderer


class APITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        # sample data
        self.index = Index.objects.create(name='NIFTY 50')
        self.index_price = IndexPrice.objects.create(
            index=self.index,
            date='2024-03-20',
            open=100.00,
            high=110.00,
            low=90.00,
            close=105.00,
            sharestraded=1000,
            turnover=100000.00
        )
        

    def test_index_list(self):
        url = reverse('indexes-list') 
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        renderer = JSONRenderer()
        data = renderer.render(response.data)
        print(data.decode('utf-8')) 
        index_prices = IndexPrice.objects.filter(index=self.index)
        for price in index_prices:
            print(f"Index Price: {price.date}, Open: {price.open}, High: {price.high}, Low: {price.low}, Close: {price.close}, Shares Traded: {price.sharestraded}, Turnover: {price.turnover}")

    def test_index_price_list(self):
        url = reverse('indexes-list')
        response = self.client.get(url)
        self.assertTrue(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    

    def test_csv_upload(self):
        url = reverse('csvupload')
        with open('test.csv', 'w') as f:
            f.write("2024-03-20,100.00,110.00,90.00,105.00,1000,100000.00")
        with open('test.csv', 'rb') as csv_file:
            data = {'file': csv_file, 'index_name': 'NIFTY 100'}
            response = self.client.post(url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)