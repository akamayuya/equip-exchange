from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("products", "0008_alter_product_fields_japanese_labels"),
    ]

    operations = [
        migrations.AlterField(
            model_name="product",
            name="location",
            field=models.CharField(blank=True, default="", max_length=255, verbose_name="表示用地域"),
        ),
    ]