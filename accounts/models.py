from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    カスタムユーザーモデル
    Django標準のUserを拡張して法人情報を追加
    """

    # 会社名
    company_name = models.CharField(
        max_length=255,
        blank=True
    )

    # 法人番号（会社識別用）
    corporate_number = models.CharField(
        max_length=50,
        blank=True,
        unique=True
    )

    # 所在地
    address = models.CharField(
        max_length=255,
        blank=True
    )

    # 審査済みフラグ（管理者が承認）
    is_verified = models.BooleanField(
        default=False
    )

    def __str__(self):
        return self.username