from django.db import models
from django.db.models import Q


class Trade(models.Model):
    ACTIVE_STATUSES = ("pending", "paid", "shipped")
    STATUS_CHOICES = [
        ("pending", "支払い待ち"),
        ("paid", "支払い済み"),
        ("shipped", "発送済み"),
        ("completed", "取引完了"),
        ("cancelled", "キャンセル"),
    ]

    product = models.ForeignKey(
        "products.Product",
        on_delete=models.CASCADE,
        related_name="trades",
        verbose_name="商品",
    )
    buyer = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="purchases",
        verbose_name="購入者",
    )
    seller = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="sales",
        verbose_name="出品者",
    )
    price = models.PositiveIntegerField(verbose_name="取引価格")
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",
        verbose_name="ステータス",
    )
    payment_method_brand = models.CharField(max_length=20, blank=True, verbose_name="支払いブランド")
    payment_method_last4 = models.CharField(max_length=4, blank=True, verbose_name="支払い下4桁")
    paid_at = models.DateTimeField(null=True, blank=True, verbose_name="支払い日時")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="取引開始日時")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新日時")

    def __str__(self):
        return f"{self.product.name} - {self.buyer.username}"

    class Meta:
        verbose_name = "取引"
        verbose_name_plural = "取引一覧"
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["product"],
                condition=Q(status__in=["pending", "paid", "shipped"]),
                name="unique_active_trade_per_product",
            )
        ]


class Message(models.Model):
    trade = models.ForeignKey(
        Trade,
        on_delete=models.CASCADE,
        related_name="messages",
        verbose_name="取引",
    )
    sender = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="sent_messages",
        verbose_name="送信者",
    )
    body = models.TextField(verbose_name="メッセージ内容")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="送信日時")

    def __str__(self):
        return f"{self.sender.username}: {self.body[:30]}"

    class Meta:
        verbose_name = "メッセージ"
        verbose_name_plural = "メッセージ一覧"
        ordering = ["created_at"]