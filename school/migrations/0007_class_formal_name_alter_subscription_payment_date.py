# Generated by Django 4.2.4 on 2024-05-29 16:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('school', '0006_subscription_transaction_count_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='class',
            name='formal_name',
            field=models.CharField(default=1, max_length=100, verbose_name='e.g form one or lower sixth'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='subscription',
            name='payment_date',
            field=models.DateField(auto_now_add=True),
        ),
    ]