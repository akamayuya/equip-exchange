from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0006_alter_user_options"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="user",
            name="address",
        ),
        migrations.RemoveField(
            model_name="user",
            name="company_name",
        ),
        migrations.RemoveField(
            model_name="user",
            name="corporate_number",
        ),
        migrations.RemoveField(
            model_name="user",
            name="is_verified",
        ),
    ]