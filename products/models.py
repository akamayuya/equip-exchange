import re
import unicodedata

from django.db import models


class Product(models.Model):
    """
    出品される機材モデル
    """

    # 商品名（機材名）
    name = models.CharField(max_length=255)

    # 商品説明（スペック・状態・付属品など）
    description = models.TextField()

    # 価格（円）
    # マイナス値を防ぐためPositiveIntegerFieldを使用
    price = models.PositiveIntegerField()

    # 商品状態の選択肢
    CONDITION_CHOICES = [
        ("S", "新品"),
        ("A", "ほぼ新品"),
        ("B", "良好"),
        ("C", "使用感あり"),
    ]

    # 商品状態
    condition = models.CharField(max_length=1, choices=CONDITION_CHOICES)

    # 機材の所在地（表示用）
    # 例：渋谷区 / 新宿区 / 横浜市など
    location = models.CharField(max_length=255)

    # 追加: より詳細な住所（町名・丁目を分ける）
    postal_code = models.CharField(max_length=20, null=True, blank=True)
    prefecture = models.CharField(max_length=100, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)  # 市区町村
    town = models.CharField(max_length=100, null=True, blank=True)  # 町名・丁目
    block = models.CharField(max_length=100, null=True, blank=True)  # 番地（丁目以下）
    address_line = models.CharField(
        max_length=255, null=True, blank=True
    )  # 建物名・部屋番号（任意、表示用）

    # 緯度（地図表示用）
    latitude = models.FloatField(null=True, blank=True)

    # 経度（地図表示用）
    longitude = models.FloatField(null=True, blank=True)

    # 出品者
    seller = models.ForeignKey(
        "accounts.User", on_delete=models.CASCADE, related_name="products"
    )

    # 売却済みフラグ
    # True = 売却済み
    # False = 販売中
    is_sold = models.BooleanField(default=False)

    # 出品日時
    created_at = models.DateTimeField(auto_now_add=True)

    # 管理画面表示
    def __str__(self):
        return self.name

    def full_address(self):
        """
        表示用のフル住所（建物名も含めることがある）
        """
        parts = []
        if self.postal_code:
            parts.append(self.postal_code)
        if self.prefecture:
            parts.append(self.prefecture)
        if self.city:
            parts.append(self.city)
        if self.town:
            parts.append(self.town)
        if self.block:
            parts.append(self.block)
        if self.address_line:
            parts.append(self.address_line)  # 表示用には建物名を含める
        if parts:
            return " ".join(parts)
        return self.location or ""

    def geocode_address(self):
        """
        ジオコーディング（緯度経度取得）に使う住所文字列。
        建物名・部屋番号（address_line）および郵便番号は除外して検索精度を向上。
        """
        parts = []
        if self.prefecture:
            parts.append(self.prefecture)
        if self.city:
            parts.append(self.city)
        if self.town:
            parts.append(self.town)
        if self.block:
            parts.append(self.block)

        raw_address = "".join(parts) if parts else (self.location or "")

        # 1. 全角数字や記号（１丁目など）を半角（1丁目）に変換
        cleaned = unicodedata.normalize("NFKC", raw_address)

        # 2. ユーザー入力の空白をすべて除去
        cleaned = cleaned.replace(" ", "")

        # 3. 数字の直後にある「丁目」「番地」「番」「号」をハイフンに置換
        # 例: 「馬場1丁目7番19号」 -> 「馬場1-7-19-」
        cleaned = re.sub(r"([0-9]+)[丁目番地番号]+", r"\1-", cleaned)

        # 4. 連続するハイフンをまとめる
        cleaned = re.sub(r"-+", "-", cleaned)

        # 5. 末尾に残ったハイフンを削除（「馬場1-7-19-」 -> 「馬場1-7-19」）
        cleaned = cleaned.rstrip("-")

        return cleaned


class ProductImage(models.Model):
    """
    商品画像モデル
    1つの商品に対して複数の画像を登録できる
    """

    # どの商品に紐づく画像か
    product = models.ForeignKey(
        "products.Product", on_delete=models.CASCADE, related_name="images"
    )

    # 画像ファイル
    image = models.ImageField(upload_to="product_images/")

    # アップロード日時
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product.name} image"


class ProductComment(models.Model):
    product = models.ForeignKey(
        "products.Product",
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name="商品",
    )
    user = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="product_comments",
        verbose_name="投稿者",
    )
    body = models.TextField(verbose_name="コメント")
    reply_to = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="replies",
        verbose_name="返信先",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="投稿日")

    def __str__(self):
        return f"{self.product.name} - {self.user.username}"

    class Meta:
        verbose_name = "商品コメント"
        verbose_name_plural = "商品コメント一覧"
        ordering = ["created_at"]
