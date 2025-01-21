# Generated by Django 5.0.2 on 2024-02-21 07:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store_app', '0015_order_payment_done_order_payment_method'),
    ]

    operations = [
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('payment_method', models.CharField(max_length=100)),
                ('payment_date', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
