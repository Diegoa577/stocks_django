# encoding: utf-8

from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
)

from django.urls import path

from stocks import views as stocks_views

urlpatterns = [
    path('stock', stocks_views.StockView.as_view(),name='stock'),
    path('api/schema/', SpectacularAPIView.as_view(), name='api-schema'),
    path(
        'api/docs/',
        SpectacularSwaggerView.as_view(url_name='api-schema'),
        name='api-docs',
    ),
]
