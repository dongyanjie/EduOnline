# Generated by Django 2.1 on 2020-08-07 02:01

from django.db import migrations, models
import users.models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_auto_20200806_1313'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='image',
            field=models.ImageField(default='images/default.png', upload_to=users.models.UserProfile.upload_to),
        ),
    ]