from django.contrib import admin

from product.models import Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("pk", "title", "description", "price", 'count')
    list_display_links = ("pk", 'title')
    search_fields = ("title",)
    ordering = ("pk",)
