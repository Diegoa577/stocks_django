# encoding: utf-8

from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
)

from django.contrib import admin
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from api import views as api_views

urlpatterns = [
    path('api/schema/', SpectacularAPIView.as_view(), name='api-schema'),
    path(
        'api/docs/',
        SpectacularSwaggerView.as_view(url_name='api-schema'),
        name='api-docs',
    ),
    path('api/token/', api_views.CustomTokenObtainPairView.as_view(), name='token'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('create/', api_views.CreateUserView.as_view(), name='create'),
    path('me/', api_views.ManageUserView.as_view(), name='me'),
    path('stock', api_views.StockView.as_view(), name='stock'),
    path('history', api_views.HistoryView.as_view(), name='history'),
    path('stats', api_views.StatsView.as_view(), name='stats'),
    path('admin', admin.site.urls),
]
