from django.contrib import admin

from product.models import Product, ProductImages, SalePrice, Specification


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("pk", "title", "description", "price", "count")
    list_display_links = ("pk", "title")
    search_fields = ("title",)
    ordering = ("pk",)


@admin.register(SalePrice)
class SalePriceAdmin(admin.ModelAdmin):
    list_display = ("pk", "salePrice", "dateFrom", "dateTo")
    list_display_links = ("pk",)
    search_fields = ("salePrice",)
    ordering = ("pk",)


@admin.register(ProductImages)
class ProductImagesAdmin(admin.ModelAdmin):
    list_display = ("pk", "src")


@admin.register(Specification)
class SpecificationAdmin(admin.ModelAdmin):
    list_display = ("name", "value")
