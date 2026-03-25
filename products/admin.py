from django.contrib import admin

from .geocoding import populate_product_coordinates
from .models import Product, ProductComment, ProductImage


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
	list_display = ("name", "seller", "price", "is_sold", "created_at")
	list_filter = ("is_sold", "condition", "prefecture")
	search_fields = ("name", "seller__username", "seller__company_name")
	readonly_fields = ("latitude", "longitude", "created_at")
	fields = (
		"name",
		"description",
		"price",
		"condition",
		"seller",
		"is_sold",
		"postal_code",
		"prefecture",
		"city",
		"town",
		"block",
		"address_line",
		"location",
		"latitude",
		"longitude",
		"created_at",
	)

	def save_model(self, request, obj, form, change):
		populate_product_coordinates(obj)
		super().save_model(request, obj, form, change)


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
	list_display = ("product", "created_at")


@admin.register(ProductComment)
class ProductCommentAdmin(admin.ModelAdmin):
	list_display = ("product", "user", "reply_to", "created_at")
	search_fields = ("product__name", "user__username", "body")
	readonly_fields = ("created_at",)
