# Generated by Django 4.2.5 on 2023-10-26 16:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0003_alter_listings_image_url'),
    ]

    operations = [
        migrations.AlterField(
            model_name='listings',
            name='starting_price',
            field=models.FloatField(),
        ),
    ]
