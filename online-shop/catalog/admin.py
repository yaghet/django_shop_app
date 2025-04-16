from django.contrib import admin

from catalog.models import Category, SubCategory


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("pk", "title")
    list_display_links = ("pk", "title")
    search_fields = ("title",)
    ordering = ("pk",)


@admin.register(SubCategory)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("pk", "title")
    list_display_links = ("pk", "title")
    search_fields = ("title",)
    ordering = ("pk",)
