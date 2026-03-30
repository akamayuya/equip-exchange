from django.db import migrations, models
from django.db.models import Q


class Migration(migrations.Migration):

    dependencies = [
        ("trades", "0004_trade_payment_fields"),
    ]

    operations = [
        migrations.AddConstraint(
            model_name="trade",
            constraint=models.UniqueConstraint(
                fields=("product",),
                condition=Q(("status__in", ["pending", "paid", "shipped"])),
                name="unique_active_trade_per_product",
            ),
        ),
    ]