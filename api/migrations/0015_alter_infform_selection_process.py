# Generated by Django 4.2.4 on 2023-08-20 03:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0014_alter_contactdetails_email_alter_contactdetails_name_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='infform',
            name='selection_process',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='selection_processINF', to='api.selectionprocess'),
        ),
    ]