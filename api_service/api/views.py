# encoding: utf-8
import requests

from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.authentication import JWTAuthentication

from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes
from api.models import UserRequestHistory, StockRequest
from api.permissions import IsSuperUser
from api.serializers import UserRequestHistorySerializer, UserSerializer,  AuthTokenSerializer, UserRequestStockSerializer




class CreateUserView(generics.CreateAPIView):
    """Create a new user in the system."""
    serializer_class = UserSerializer

class ManageUserView(generics.RetrieveUpdateAPIView):
    """Manage the authenticated user."""
    serializer_class = UserSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        """Retrieve and return authenticated user"""
        return self.request.user

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = AuthTokenSerializer

class StockView(APIView):
    """
    Endpoint to allow users to query stocks
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserRequestStockSerializer
    @extend_schema(parameters=[
        OpenApiParameter('s', OpenApiTypes.STR, OpenApiParameter.QUERY, description='Stock symbol')
    ])
    def get(self, request, *args, **kwargs):
        stock_code = request.query_params.get('s')
        
        try:
            stock_service_url = 'http://localhost:8001/stock'  # Update with your stock_service URL
            response = requests.get(f'{stock_service_url}?s={stock_code}')
            
            response.raise_for_status()
            stock_data = response.json()
        except requests.HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')
            return Response({'detail': 'An error occurred while retrieving stock data.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as err:
            print(f'Other error occurred: {err}')
            return Response({'detail': 'An error occurred while retrieving stock data.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        stock = UserRequestHistory(user=request.user, **stock_data)
        stock.save()

        # Serialize the stock data for the response
        serializer = UserRequestStockSerializer(stock)
        return Response(serializer.data, status=status.HTTP_200_OK)


class HistoryView(generics.ListAPIView):
    """
    Returns queries made by current user.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request, format=None):
        queryset = UserRequestHistory.objects.filter(user=request.user).order_by('-date')
        serializer_class = UserRequestHistorySerializer(queryset, many=True)
        return Response(serializer_class.data, status=status.HTTP_200_OK)


class StatsView(APIView):
    """
    Allows super users to see which are the most queried stocks.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsSuperUser]
    # TODO: Implement the query needed to get the top-5 stocks as described in the README, and return
    # the results to the user.
    def get(self, request, *args, **kwargs):
        top_stocks = StockRequest.objects.order_by('-times_requested')[:5]
        data = [{"stock": stock.symbol, "times_requested": stock.times_requested} for stock in top_stocks]
        return Response(data, status=status.HTTP_200_OK)
