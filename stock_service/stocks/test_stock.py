from django.test import SimpleTestCase 
from rest_framework.test import APIClient
from django.urls import reverse
from rest_framework import status
import requests_mock
import datetime

# Create your tests here.

class StockViewConsumeTest(SimpleTestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('stock')

    @requests_mock.Mocker()
    def test_stock_view_consume(self, mock_req):
        mock_req.get('https://stooq.com/q/l/?s=aapl.us&f=sd2t2ohlcvn&h&e=csv', 
                    text='Symbol,Date,time,,Open,High,Low,Close,Volume,Name\nAAPL.US,2023-06-24,22:00:16,123.66,123.66,122.49,123.49,53116996,APPLE\n')
        response = self.client.get(self.url + '?s=aapl.us')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(response.data, {
            "name": "APPLE",
            "symbol": "AAPL.US",
            "date": datetime.datetime(2023, 6, 24, 22, 0, 16),
            "open": "123.66",
            "high": "123.66",
            "low": "122.49",
            "close": "123.49"
        })

    @requests_mock.Mocker()
    def test_stock_view_consume_invalid_symbol(self, mock_req):
        mock_req.get('https://stooq.com/q/l/?s=invalid&f=sd2t2ohlcvn&h&e=csv', text='\n')
        response = self.client.get(self.url + '?s=invalid')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)