from django.urls import path

from product.views import ProductDetailView, ProductReviewView

app_name = "product"

urlpatterns = [
    path("product/<int:id>/", ProductDetailView.as_view()),
    path("product/<int:id>/reviews", ProductReviewView.as_view()),
]
