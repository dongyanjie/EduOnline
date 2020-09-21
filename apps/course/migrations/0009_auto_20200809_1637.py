# Generated by Django 2.1 on 2020-08-09 08:37

import course.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('organization', '0007_teacher_image'),
        ('course', '0008_auto_20200809_1624'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='teacher',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='organization.Teacher', verbose_name='讲师/教授2'),
        ),
        migrations.AddField(
            model_name='course',
            name='teacher_tell',
            field=models.CharField(default='', max_length=300, verbose_name='老师告诉你'),
        ),
        migrations.AddField(
            model_name='course',
            name='youneed_know',
            field=models.CharField(default='', max_length=300, verbose_name='课程须知'),
        ),
        migrations.AlterField(
            model_name='courseresource',
            name='download',
            field=models.FileField(max_length=200, upload_to=course.models.CourseResource.upload_to, verbose_name='资源文件'),
        ),
    ]
