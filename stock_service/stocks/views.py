# encoding: utf-8
import requests
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import csv
from io import StringIO
from datetime import datetime



class StockView(APIView):
    """
    Receives stock requests from the API service.
    """
    @extend_schema(parameters=[
        OpenApiParameter('s', OpenApiTypes.STR, OpenApiParameter.QUERY, description='Stock symbol')
    ])
    def get(self, request, *args, **kwargs):
        stock_code = request.query_params.get('s')

        if not stock_code:
            return Response({"detail": "Missing stock symbol."}, status=status.HTTP_400_BAD_REQUEST)
        
        stock_url = f'https://stooq.com/q/l/?s={stock_code}&f=sd2t2ohlcvn&h&e=csv'
        response = requests.get(stock_url)

        # Parse the CSV response
        csv_data = csv.reader(StringIO(response.text))
        data = list(csv_data)

        if not data or len(data) < 2:
            return Response({"detail": "Stock not found."}, status=404)
        
        stock_data = {
            "name": data[1][8],
            "symbol": data[1][0],
            "date": datetime.strptime(f"{data[1][1]}T{data[1][2]}Z", "%Y-%m-%dT%H:%M:%SZ"), #The challenge do not specify which date take so we assume the date that we received from the request
            "open": data[1][3],
            "high": data[1][4],
            "low": data[1][5],
            "close": data[1][6]
        }


        # TODO: Make request to the stooq.com API, parse the response and send it to the API service.
        return Response(stock_data, status=status.HTTP_200_OK)
