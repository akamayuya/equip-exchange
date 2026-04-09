from django.contrib.auth.models import AbstractUser
from django.db import models


class Company(models.Model):
    name = models.CharField(max_length=255, verbose_name="会社名")
    corporate_number = models.CharField(max_length=50, null=True, blank=True, unique=True, verbose_name="法人番号")
    address = models.CharField(max_length=255, blank=True, verbose_name="所在地")
    is_verified = models.BooleanField(default=False, verbose_name="審査済み")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="登録日時")

    class Meta:
        verbose_name = "法人"
        verbose_name_plural = "法人"
        ordering = ["name", "id"]

    def __str__(self):
        return self.name or f"法人 {self.pk}"


class User(AbstractUser):
    """
    カスタムユーザーモデル
    Django標準のUserを拡張して法人所属情報を追加
    """
    company = models.ForeignKey(
        "accounts.Company",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="users",
        verbose_name="所属法人",
    )
    is_company_admin = models.BooleanField(default=True, verbose_name="法人管理者")

    class Meta:
        verbose_name = "ユーザー"
        verbose_name_plural = "ユーザー"

    def japanese_full_name(self):
        parts = [part for part in [self.last_name, self.first_name] if part]
        return " ".join(parts).strip()

    def __str__(self):
        return self.username


class PaymentMethod(models.Model):
    BRAND_CHOICES = [
        ("visa", "Visa"),
        ("mastercard", "Mastercard"),
        ("jcb", "JCB"),
        ("amex", "American Express"),
    ]

    user = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="payment_methods",
        verbose_name="ユーザー",
    )
    cardholder_name = models.CharField(max_length=255, verbose_name="カード名義")
    brand = models.CharField(max_length=20, choices=BRAND_CHOICES, verbose_name="ブランド")
    last4 = models.CharField(max_length=4, verbose_name="下4桁")
    exp_month = models.PositiveSmallIntegerField(verbose_name="有効期限月")
    exp_year = models.PositiveSmallIntegerField(verbose_name="有効期限年")
    token = models.CharField(max_length=64, unique=True, verbose_name="モックトークン")
    is_default = models.BooleanField(default=False, verbose_name="デフォルト")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="登録日時")

    class Meta:
        ordering = ["-is_default", "-created_at"]
        verbose_name = "支払い方法"
        verbose_name_plural = "支払い方法"

    def __str__(self):
        return f"{self.get_brand_display()} **** {self.last4}"

    @property
    def masked_number(self):
        return f"**** **** **** {self.last4}"