from django.urls import path

from basket.views import BasketItemAPIView

urlpatterns = [
    path("basket/", BasketItemAPIView.as_view(), name="basket"),
    path("basket", BasketItemAPIView.as_view(), name="basket"),
]
