# Generated by Django 4.2.5 on 2023-11-01 09:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('network', '0002_user_photo'),
    ]

    operations = [
        migrations.RenameField(
            model_name='user',
            old_name='photo',
            new_name='avatar',
        ),
    ]