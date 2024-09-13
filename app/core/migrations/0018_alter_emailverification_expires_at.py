# Generated by Django 3.2.25 on 2024-09-13 21:57

import core.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0017_auto_20240913_2153'),
    ]

    operations = [
        migrations.AlterField(
            model_name='emailverification',
            name='expires_at',
            field=models.DateTimeField(default=core.models.get_email_verification_expiration_date),
        ),
    ]
