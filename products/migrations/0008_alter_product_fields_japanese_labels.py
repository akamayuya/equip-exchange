from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("products", "0007_alter_product_options_alter_productimage_options"),
    ]

    operations = [
        migrations.AlterField(
            model_name="product",
            name="name",
            field=models.CharField(max_length=255, verbose_name="商品名"),
        ),
        migrations.AlterField(
            model_name="product",
            name="description",
            field=models.TextField(verbose_name="商品説明"),
        ),
        migrations.AlterField(
            model_name="product",
            name="price",
            field=models.PositiveIntegerField(verbose_name="価格"),
        ),
        migrations.AlterField(
            model_name="product",
            name="condition",
            field=models.CharField(choices=[("S", "新品"), ("A", "ほぼ新品"), ("B", "良好"), ("C", "使用感あり")], max_length=1, verbose_name="状態"),
        ),
        migrations.AlterField(
            model_name="product",
            name="location",
            field=models.CharField(max_length=255, verbose_name="表示用地域"),
        ),
        migrations.AlterField(
            model_name="product",
            name="postal_code",
            field=models.CharField(blank=True, max_length=20, null=True, verbose_name="郵便番号"),
        ),
        migrations.AlterField(
            model_name="product",
            name="prefecture",
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name="都道府県"),
        ),
        migrations.AlterField(
            model_name="product",
            name="city",
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name="市区町村"),
        ),
        migrations.AlterField(
            model_name="product",
            name="town",
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name="町名"),
        ),
        migrations.AlterField(
            model_name="product",
            name="block",
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name="丁目・番地・号"),
        ),
        migrations.AlterField(
            model_name="product",
            name="address_line",
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name="建物名・部屋番号"),
        ),
        migrations.AlterField(
            model_name="product",
            name="latitude",
            field=models.FloatField(blank=True, null=True, verbose_name="緯度"),
        ),
        migrations.AlterField(
            model_name="product",
            name="longitude",
            field=models.FloatField(blank=True, null=True, verbose_name="経度"),
        ),
        migrations.AlterField(
            model_name="product",
            name="seller",
            field=models.ForeignKey(on_delete=models.deletion.CASCADE, related_name="products", to="accounts.user", verbose_name="出品者"),
        ),
        migrations.AlterField(
            model_name="product",
            name="is_sold",
            field=models.BooleanField(default=False, verbose_name="売却済み"),
        ),
        migrations.AlterField(
            model_name="product",
            name="created_at",
            field=models.DateTimeField(auto_now_add=True, verbose_name="出品日時"),
        ),
        migrations.AlterField(
            model_name="productimage",
            name="image",
            field=models.ImageField(upload_to="product_images/", verbose_name="画像"),
        ),
        migrations.AlterField(
            model_name="productimage",
            name="created_at",
            field=models.DateTimeField(auto_now_add=True, verbose_name="登録日時"),
        ),
    ]