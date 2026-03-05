from django.db import models


class Product(models.Model):
    """
    出品される機材モデル
    """

    # 商品名（機材名）
    name = models.CharField(
        max_length=255
    )

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
    condition = models.CharField(
        max_length=1,
        choices=CONDITION_CHOICES
    )

    # 機材の所在地（市区町村など）
    location = models.CharField(
        max_length=255
    )

    # 出品者（Userと紐付け）
    seller = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE
    )
    
    # 売却状態
    # Trueの場合は「売却済み」
    # Falseの場合は「販売中」
    # 商品一覧で「売れている商品」を除外するために使用
    is_sold = models.BooleanField(
        default=False
    )

    # 売却済みフラグ
    is_sold = models.BooleanField(
        default=False
    )

    # 出品日時
    created_at = models.DateTimeField(
        auto_now_add=True
    )

    # 管理画面表示
    def __str__(self):
        return self.name
    
    
class ProductImage(models.Model):
    # 商品画像モデル
    # 1つの商品に対して複数の画像を登録できる

    # どの商品に紐づく画像か
    product = models.ForeignKey(
        "products.Product",
        on_delete=models.CASCADE,
        related_name="images"
    )

    # 画像ファイル
    # 将来的にAWS S3へ保存する想定
    image = models.ImageField(
        upload_to="product_images/"
    )

    # アップロード日時
    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.product.name} image"