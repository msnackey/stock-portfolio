# Generated by Django 4.1.3 on 2022-12-13 08:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0008_alter_stock_shares_alter_stock_value'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='target',
            field=models.DecimalField(decimal_places=0, max_digits=3),
        ),
    ]
