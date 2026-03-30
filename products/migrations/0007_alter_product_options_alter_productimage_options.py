from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("products", "0006_productcomment"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="product",
            options={"verbose_name": "商品", "verbose_name_plural": "商品"},
        ),
        migrations.AlterModelOptions(
            name="productimage",
            options={"verbose_name": "商品画像", "verbose_name_plural": "商品画像"},
        ),
    ]