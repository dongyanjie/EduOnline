# PEP8规范  第一区域自带，第二区域第三方
from datetime import datetime

from django.db import models
from django.contrib.auth.models import AbstractUser


# 用户信息表 ,继承系统user表
class UserProfile(AbstractUser):
    # 重新定义上传文件的路径
    def upload_to(self, filename):
        filename = filename.split('.')[-2] + '_' + str(datetime.now().strftime("%Y%m%d%H%M%S")) + '.' + \
                   filename.split('.')[-1]
        return '/'.join(['images', self.nick_name, filename])

    gender_choices = (
        ('male', '男'),
        ('female', '女')
    )

    nick_name = models.CharField('昵称', max_length=50, default='')
    birthday = models.DateField('生日', null=True, blank=True)
    gender = models.CharField('性别', max_length=10, choices=gender_choices, default='female')
    address = models.CharField('地址', max_length=150, default='')
    mobile = models.CharField('手机号', max_length=11, null=True, blank=True)
    image = models.ImageField(upload_to=upload_to, max_length=100, default='images/default.png')

    class Meta:
        verbose_name = '用户信息'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.username


# 邮箱验证码表
class EmailVerifyRecord(models.Model):
    send_type_choices = (
        ('register', '注册'),
        ('forget', '找回密码'),
        ('update_email', '修改邮箱'),
    )

    code = models.CharField('验证码', max_length=20)
    email = models.EmailField('邮箱', max_length=50)
    send_type = models.CharField(choices=send_type_choices, max_length=50)
    send_time = models.DateTimeField('发送时间', auto_now_add=True)

    class Meta:
        verbose_name = '邮箱验证码'
        verbose_name_plural = verbose_name


# 轮播图表
# image上传到哪里;url是图片链接的路径;index控制轮播图的播放顺序
class Banner(models.Model):
    title = models.CharField('标题', max_length=100)
    image = models.ImageField('轮播图', upload_to='banner/%Y%m', max_length=100)
    url = models.URLField('访问地址', max_length=200, null=True, blank=True)
    index = models.IntegerField('顺序', default=100)
    add_time = models.DateTimeField('添加时间', auto_now_add=True)

    class Meta:
        verbose_name = '轮播图'
        verbose_name_plural = verbose_name
