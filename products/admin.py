from django.contrib import admin

from .geocoding import populate_product_coordinates
from .models import Product, ProductComment, ProductImage


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
	list_display = ("product_name", "seller_name", "price", "sold_status", "created_at")
	list_filter = ("is_sold", "condition")
	search_fields = ("name", "seller__username", "seller__company__name", "seller__company__address")
	readonly_fields = ("latitude", "longitude", "created_at")
	fields = (
		"name",
		"description",
		"price",
		"condition",
		"seller",
		"is_sold",
		"latitude",
		"longitude",
		"created_at",
	)

	def save_model(self, request, obj, form, change):
		populate_product_coordinates(obj)
		super().save_model(request, obj, form, change)

	@admin.display(description="商品名", ordering="name")
	def product_name(self, obj):
		return obj.name

	@admin.display(description="出品者", ordering="seller__username")
	def seller_name(self, obj):
		return obj.seller.username

	@admin.display(description="状態", ordering="is_sold")
	def sold_status(self, obj):
		if not obj.is_sold:
			return "出品中"
		if obj.trades.filter(status__in=("pending", "paid", "shipped")).exists():
			return "取引中"
		return "売却済み"


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
	list_display = ("product", "created_at")


@admin.register(ProductComment)
class ProductCommentAdmin(admin.ModelAdmin):
	list_display = ("product", "user", "reply_to", "created_at")
	search_fields = ("product__name", "user__username", "body")
	readonly_fields = ("created_at",)
