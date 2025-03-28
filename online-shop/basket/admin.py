from django.contrib import admin

from basket.models import BasketItem, Basket


@admin.register(Basket)
class BasketAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at')
    list_filter = ('user',)
    search_fields = ('user',)


@admin.register(BasketItem)
class BasketItemAdmin(admin.ModelAdmin):
    list_display = ("id", "product", "amount")
    list_filter = ("product",)
    search_fields = ("product",)
    ordering = ("id",)
