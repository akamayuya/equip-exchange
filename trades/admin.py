from django.contrib import admin
from .models import Message, Trade

@admin.register(Trade)
class TradeAdmin(admin.ModelAdmin):
	list_display = ("product", "buyer", "seller", "price", "status", "payment_method_brand", "payment_method_last4", "paid_at")
	list_filter = ("status", "payment_method_brand")
	search_fields = ("product__name", "buyer__username", "seller__username")


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
	list_display = ("trade", "sender", "created_at")
	search_fields = ("trade__product__name", "sender__username", "body")
	readonly_fields = ("created_at",)
