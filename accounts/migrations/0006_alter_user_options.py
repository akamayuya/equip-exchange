from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0005_company_user_company_and_more"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="user",
            options={"verbose_name": "ユーザー", "verbose_name_plural": "ユーザー"},
        ),
    ]