from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("trades", "0003_alter_trade_options_trade_seller_trade_updated_at_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="trade",
            name="paid_at",
            field=models.DateTimeField(blank=True, null=True, verbose_name="支払い日時"),
        ),
        migrations.AddField(
            model_name="trade",
            name="payment_method_brand",
            field=models.CharField(blank=True, max_length=20, verbose_name="支払いブランド"),
        ),
        migrations.AddField(
            model_name="trade",
            name="payment_method_last4",
            field=models.CharField(blank=True, max_length=4, verbose_name="支払い下4桁"),
        ),
    ]