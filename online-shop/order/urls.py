from django.urls import path

from order.views import OrderDetailView, OrdersCreateView, PaymentView

app_name = "order"

urlpatterns = [
    path("orders", OrdersCreateView.as_view(), name="create-orders"),
    path("order/<int:id>", OrderDetailView.as_view(), name="create-order-id"),
    path("payment/<int:id>", PaymentView.as_view(), name="create-payment"),
]
