from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0003_remove_user_created_at_alter_user_corporate_number"),
    ]

    operations = [
        migrations.CreateModel(
            name="PaymentMethod",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("cardholder_name", models.CharField(max_length=255, verbose_name="カード名義")),
                ("brand", models.CharField(choices=[("visa", "Visa"), ("mastercard", "Mastercard"), ("jcb", "JCB"), ("amex", "American Express")], max_length=20, verbose_name="ブランド")),
                ("last4", models.CharField(max_length=4, verbose_name="下4桁")),
                ("exp_month", models.PositiveSmallIntegerField(verbose_name="有効期限月")),
                ("exp_year", models.PositiveSmallIntegerField(verbose_name="有効期限年")),
                ("token", models.CharField(max_length=64, unique=True, verbose_name="モックトークン")),
                ("is_default", models.BooleanField(default=False, verbose_name="デフォルト")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="登録日時")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="payment_methods", to="accounts.user", verbose_name="ユーザー")),
            ],
            options={
                "ordering": ["-is_default", "-created_at"],
                "verbose_name": "支払い方法",
                "verbose_name_plural": "支払い方法",
            },
        ),
    ]