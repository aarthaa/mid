# Generated by Django 5.1.5 on 2025-01-24 05:45

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store_app', '0019_order_total_price_alter_order_address_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderitem',
            name='images',
            field=models.ImageField(blank=True, default='', upload_to='Product_images/Order_Img'),
        ),
        migrations.AlterField(
            model_name='orderitem',
            name='order',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='order_items', to='store_app.order'),
        ),
        migrations.AlterField(
            model_name='orderitem',
            name='quantity',
            field=models.CharField(default='0', max_length=20),
        ),
        migrations.AlterField(
            model_name='orderitem',
            name='total',
            field=models.CharField(default='0', max_length=100),
        ),
    ]
