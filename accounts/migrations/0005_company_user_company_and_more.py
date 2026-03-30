from django.db import migrations, models
import django.db.models.deletion


def create_companies_for_existing_users(apps, schema_editor):
    Company = apps.get_model("accounts", "Company")
    User = apps.get_model("accounts", "User")

    company_cache = {}

    for user in User.objects.all().order_by("id"):
        company_name = (user.company_name or "").strip()
        corporate_number = (user.corporate_number or "").strip()
        address = (user.address or "").strip()

        if corporate_number:
            cache_key = ("corporate_number", corporate_number)
        elif company_name:
            cache_key = ("company_name", company_name)
        else:
            cache_key = ("user", user.id)

        company = company_cache.get(cache_key)
        if company is None:
            company = Company.objects.create(
                name=company_name or f"未設定法人 {user.id}",
                corporate_number=corporate_number or None,
                address=address,
                is_verified=user.is_verified,
            )
            company_cache[cache_key] = company

        user.company_id = company.id
        user.is_company_admin = True
        user.save(update_fields=["company", "is_company_admin"])


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0004_paymentmethod"),
    ]

    operations = [
        migrations.CreateModel(
            name="Company",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=255, verbose_name="会社名")),
                ("corporate_number", models.CharField(blank=True, max_length=50, null=True, unique=True, verbose_name="法人番号")),
                ("address", models.CharField(blank=True, max_length=255, verbose_name="所在地")),
                ("is_verified", models.BooleanField(default=False, verbose_name="審査済み")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="登録日時")),
            ],
            options={
                "verbose_name": "法人",
                "verbose_name_plural": "法人",
                "ordering": ["name", "id"],
            },
        ),
        migrations.AddField(
            model_name="user",
            name="company",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="users", to="accounts.company", verbose_name="所属法人"),
        ),
        migrations.AddField(
            model_name="user",
            name="is_company_admin",
            field=models.BooleanField(default=True, verbose_name="法人管理者"),
        ),
        migrations.RunPython(create_companies_for_existing_users, migrations.RunPython.noop),
    ]