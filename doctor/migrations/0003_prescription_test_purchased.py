# Generated by Django 5.2 on 2025-06-15 09:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("doctor", "0002_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="prescription_test",
            name="purchased",
            field=models.BooleanField(default=False),
        ),
    ]
