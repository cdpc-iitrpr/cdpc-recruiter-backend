# Generated by Django 4.2.4 on 2023-08-12 11:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_rename_users_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contactdetails',
            name='mobile',
            field=models.TextField(blank=True, null=True),
        ),
    ]
