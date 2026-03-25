from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0003_remove_user_created_at_alter_user_corporate_number"),
        ("products", "0005_product_block_product_town"),
    ]

    operations = [
        migrations.CreateModel(
            name="ProductComment",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("body", models.TextField(verbose_name="コメント")),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="投稿日"),
                ),
                (
                    "product",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="comments",
                        to="products.product",
                        verbose_name="商品",
                    ),
                ),
                (
                    "reply_to",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="replies",
                        to="products.productcomment",
                        verbose_name="返信先",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="product_comments",
                        to="accounts.user",
                        verbose_name="投稿者",
                    ),
                ),
            ],
            options={
                "verbose_name": "商品コメント",
                "verbose_name_plural": "商品コメント一覧",
                "ordering": ["created_at"],
            },
        ),
    ]