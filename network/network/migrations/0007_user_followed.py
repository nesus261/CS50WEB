# Generated by Django 4.2.5 on 2023-11-02 18:16

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('network', '0006_remove_post_likes_post_likes'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='followed',
            field=models.ManyToManyField(blank=True, related_name='followers', to=settings.AUTH_USER_MODEL),
        ),
    ]