from django.urls import path
from catalog.views import CategoryListView, CatalogListAPIView

app_name = "catalog"

urlpatterns = [
    path("categories", CategoryListView.as_view(), name="api-categories-list"),
    path("catalog", CatalogListAPIView.as_view(), name="category-list"),
]