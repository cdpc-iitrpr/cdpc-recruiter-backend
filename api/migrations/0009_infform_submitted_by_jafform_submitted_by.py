# Generated by Django 4.2.4 on 2023-08-16 11:06

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0008_infform_versiontitle_jafform_versiontitle'),
    ]

    operations = [
        migrations.AddField(
            model_name='infform',
            name='submitted_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='jafform',
            name='submitted_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
