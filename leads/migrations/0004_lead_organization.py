# Generated by Django 4.2.2 on 2023-06-27 12:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('leads', '0003_lead_manager_status_group'),
    ]

    operations = [
        migrations.AddField(
            model_name='lead',
            name='organization',
            field=models.CharField(default=None, max_length=100, null=True),
        ),
    ]
