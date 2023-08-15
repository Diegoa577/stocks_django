from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase,APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from api.models import UserRequestHistory, StockRequest
from datetime import timedelta
from django.utils import timezone
import requests_mock
import datetime

def create_user(**params):
    """Create and return a new user."""
    return get_user_model().objects.create_user(**params)

def create_superuser(**params):
    """Create and return a new user."""
    return get_user_model().objects.create_superuser(**params)


class StockViewTestCase(APITestCase):
    def setUp(self):
        self.user = create_user(
            email='test@example.com',
            password='testpass123',
            name='Test Name',
        )

        self.client = APIClient()
        
        self.user_access_token = RefreshToken.for_user(self.user)

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user_access_token.access_token}')

    @requests_mock.Mocker()
    def test_stock_view(self, mock_req):
        self.url = reverse('stock')
        mock_req.get('http://localhost:8001/stock', 
                    json={"name": "APPLE", "symbol": "AAPL.US", "date":"2021-04-01T19:20:30Z", "open": "123.66", "high": "123.66", "low": "122.49", "close": "123"})
        response = self.client.get(self.url + '?s=aapl.us')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        expect_value = {
            "name": "APPLE",
            "symbol": "AAPL.US",
            "open": 123.66,
            "high": 123.66,
            "low": 122.49,
            "close": 123.0
        }

        self.assertEqual(response.data, expect_value)

    @requests_mock.Mocker()
    def test_stock_view_invalid_symbol(self, mock_req):
        self.url = reverse('stock')
        mock_req.get('http://localhost:8001/stock', 
                     status_code=status.HTTP_404_NOT_FOUND)
        response = self.client.get(self.url + '?s=invalid')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


    def test_stock_history_view(self):
        # Create some stock objects associated with the user
        now = timezone.now()
        stock1 = UserRequestHistory.objects.create(user=self.user, symbol='AAPL.US', name='Apple', open=123.66, high=123.66, low=122.49, close=123, date=now)
        stock2 = UserRequestHistory.objects.create(user=self.user, symbol='MSFT.US', name='Microsoft', open=245.22, high=247.38, low=243.79, close=245.17, date=now - timedelta(days=1))
        stock3 = UserRequestHistory.objects.create(user=self.user, symbol='MSFT.US', name='Microsoft', open=240.66, high=250.66, low=220.49, close=240, date=now + timedelta(days=1))
        stock4 = UserRequestHistory.objects.create(user=self.user, symbol='AAPL.US', name='Apple', open=123.66, high=123.66, low=122.49, close=123, date=now - timedelta(hours=1))

        url = reverse('history')  # Assuming you have the URL name defined as 'history' in your urls.py

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected_data = [
            {'date': stock3.date.strftime('%Y-%m-%dT%H:%M:%S.%fZ'), 'name': 'Microsoft', 'symbol': 'MSFT.US', 'open': 240.66, 'high': 250.66, 'low': 220.49, 'close': 240.00},
            {'date': stock1.date.strftime('%Y-%m-%dT%H:%M:%S.%fZ'), 'name': 'Apple', 'symbol': 'AAPL.US', 'open': 123.66, 'high': 123.66, 'low': 122.49, 'close': 123.00},
            {'date': stock4.date.strftime('%Y-%m-%dT%H:%M:%S.%fZ'), 'name': 'Apple', 'symbol': 'AAPL.US', 'open': 123.66, 'high': 123.66, 'low': 122.49, 'close': 123.00},
            {'date': stock2.date.strftime('%Y-%m-%dT%H:%M:%S.%fZ'), 'name': 'Microsoft', 'symbol': 'MSFT.US', 'open': 245.22, 'high': 247.38, 'low': 243.79, 'close': 245.17},
        ]
        self.assertEqual(response.data, expected_data)

    def test_stock_history_view_empty(self):
        # Create some stock objects associated with the user

        url = reverse('history')  # Assuming you have the URL name defined as 'history' in your urls.py

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(response.data, [])

    def test_stock_stats_view_no_super_user(self):
        
        url = reverse('stats')  # Assuming you have the URL name defined as 'stats' in your urls.py

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

class StockViewTestCase_super_user(APITestCase):
    def setUp(self):
        self.user = create_superuser(
            email='test@example.com',
            password='testpass123',
        )

        self.client = APIClient()
        
        self.user_access_token = RefreshToken.for_user(self.user)

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user_access_token.access_token}')

    def test_stock_stats_view_user(self):
        # Create some stock requests

        StockRequest.objects.create(symbol='AAPL.US', times_requested=5)
        StockRequest.objects.create(symbol='MSFT.US', times_requested=2)
        StockRequest.objects.create(symbol='NDAQ.US', times_requested=30)
        StockRequest.objects.create(symbol='AAON.US', times_requested=1)
        StockRequest.objects.create(symbol='GOOGL.US', times_requested=24)
        StockRequest.objects.create(symbol='AMZN.US', times_requested=3)

        url = reverse('stats')  # Assuming you have the URL name defined as 'stats' in your urls.py

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        expected_data = [
            {'stock': 'NDAQ.US', 'times_requested': 30}, 
            {'stock': 'GOOGL.US', 'times_requested': 24}, 
            {'stock': 'AAPL.US', 'times_requested': 5}, 
            {'stock': 'AMZN.US', 'times_requested': 3}, 
            {'stock': 'MSFT.US', 'times_requested': 2}]
        
        self.assertEqual(response.data, expected_data)

class StockNoAuthTestCase(APITestCase):
    def test_stock_view_no_auth(self):

        url = reverse('stock')  # Assuming you have the URL name defined as 'history' in your urls.py

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_stock_history_view_no_auth(self):

        url = reverse('history')  # Assuming you have the URL name defined as 'history' in your urls.py

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_stock_stats_view_no_auth(self):
        url = reverse('stats')  # Assuming you have the URL name defined as 'stats' in your urls.py

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)