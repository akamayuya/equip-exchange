from django.contrib import admin
from .models import Message, Trade


@admin.register(Trade)
class TradeAdmin(admin.ModelAdmin):
	list_display = ("product", "buyer", "seller", "price", "status_display", "payment_method_brand", "payment_method_last4", "paid_at")
	list_filter = ("status", "payment_method_brand")
	search_fields = ("product__name", "buyer__username", "seller__username")
	readonly_fields = ("product", "buyer", "seller", "price", "payment_method_brand", "payment_method_last4", "paid_at", "created_at", "updated_at")

	@admin.display(description="ステータス", ordering="status")
	def status_display(self, obj):
		return obj.get_status_display()

	def save_model(self, request, obj, form, change):
		super().save_model(request, obj, form, change)
		if change and "status" in form.changed_data:
			if obj.status == "cancelled":
				obj.product.is_sold = False
				obj.product.save(update_fields=["is_sold"])
			elif obj.status in Trade.ACTIVE_STATUSES:
				obj.product.is_sold = True
				obj.product.save(update_fields=["is_sold"])


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
	list_display = ("trade", "sender", "created_at")
	search_fields = ("trade__product__name", "sender__username", "body")
	readonly_fields = ("created_at",)
