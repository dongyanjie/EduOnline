# Generated by Django 2.1 on 2020-08-10 11:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('organization', '0007_teacher_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='teacher',
            name='age',
            field=models.IntegerField(blank=True, null=True, verbose_name='年龄'),
        ),
    ]