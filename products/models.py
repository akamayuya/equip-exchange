from django.db import models


class Product(models.Model):
    """
    出品される機材モデル
    """

    # 商品名（機材名）
    name = models.CharField(max_length=255, verbose_name="商品名")

    # 商品説明（スペック・状態・付属品など）
    description = models.TextField(verbose_name="商品説明")

    # 価格（円）
    # マイナス値を防ぐためPositiveIntegerFieldを使用
    price = models.PositiveIntegerField(verbose_name="価格")

    # 商品状態の選択肢
    CONDITION_CHOICES = [
        ("S", "新品"),
        ("A", "ほぼ新品"),
        ("B", "良好"),
        ("C", "使用感あり"),
    ]

    # 商品状態
    condition = models.CharField(max_length=1, choices=CONDITION_CHOICES, verbose_name="状態")

    # 機材の所在地（表示用）
    # 例：渋谷区 / 新宿区 / 横浜市など
    location = models.CharField(max_length=255, blank=True, default="", verbose_name="表示用地域")

    # 追加: より詳細な住所（町名・丁目を分ける）
    postal_code = models.CharField(max_length=20, null=True, blank=True, verbose_name="郵便番号")
    prefecture = models.CharField(max_length=100, null=True, blank=True, verbose_name="都道府県")
    city = models.CharField(max_length=100, null=True, blank=True, verbose_name="市区町村")  # 市区町村
    town = models.CharField(max_length=100, null=True, blank=True, verbose_name="町名")  # 町名・丁目
    block = models.CharField(max_length=100, null=True, blank=True, verbose_name="丁目・番地・号")  # 番地（丁目以下）
    address_line = models.CharField(
        max_length=255, null=True, blank=True, verbose_name="建物名・部屋番号"
    )  # 建物名・部屋番号（任意、表示用）

    # 緯度（地図表示用）
    latitude = models.FloatField(null=True, blank=True, verbose_name="緯度")

    # 経度（地図表示用）
    longitude = models.FloatField(null=True, blank=True, verbose_name="経度")

    # 出品者
    seller = models.ForeignKey(
        "accounts.User", on_delete=models.CASCADE, related_name="products", verbose_name="出品者"
    )

    # 売却済みフラグ
    # True = 売却済み
    # False = 販売中
    is_sold = models.BooleanField(default=False, verbose_name="売却済み")

    # 出品日時
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="出品日時")

    # 管理画面表示
    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "商品"
        verbose_name_plural = "商品"

    def full_address(self):
        seller = getattr(self, "seller", None)
        seller_company = getattr(seller, "company", None) if seller else None
        return getattr(seller_company, "address", "") or ""

    def geocode_address(self):
        return self.full_address()


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
    image = models.ImageField(upload_to="product_images/", verbose_name="画像")

    # アップロード日時
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="登録日時")

    def __str__(self):
        return f"{self.product.name} image"

    class Meta:
        verbose_name = "商品画像"
        verbose_name_plural = "商品画像"


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
