from django.db import models


class Trade(models.Model):
    """
    商品の取引情報
    """

    # 取引される商品
    product = models.ForeignKey(
        "products.Product",
        on_delete=models.CASCADE
    )

    # 購入者
    buyer = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="purchases"
    )

    # 取引価格
    price = models.PositiveIntegerField()

    # 取引ステータス
    STATUS_CHOICES = [
        ("pending", "取引中"),
        ("completed", "取引完了"),
        ("cancelled", "キャンセル"),
    ]

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending"
    )

    # 取引開始日時
    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.product.name} - {self.buyer.username}"