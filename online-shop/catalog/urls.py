from django.urls import path

from catalog.views import (
    BannerListView,
    CatalogListAPIView,
    CategoryListView,
    LimitedProductsView,
    PopularProductsView,
    SalesView,
)

app_name = "catalog"

urlpatterns = [
    path("categories", CategoryListView.as_view(), name="api-categories-list"),
    path("catalog", CatalogListAPIView.as_view(), name="category-list"),
    path("products/popular/", PopularProductsView.as_view(), name="popular_products"),
    path("products/limited/", LimitedProductsView.as_view(), name="limited_products"),
    path("sales/", SalesView.as_view(), name="sales_list"),
    path("banners/", BannerListView.as_view(), name="banners_list"),
]
