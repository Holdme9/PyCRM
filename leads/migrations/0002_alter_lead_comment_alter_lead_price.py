# Generated by Django 4.2.2 on 2023-06-21 11:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('leads', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lead',
            name='comment',
            field=models.TextField(blank=True, default=None),
        ),
        migrations.AlterField(
            model_name='lead',
            name='price',
            field=models.IntegerField(blank=True),
        ),
    ]
