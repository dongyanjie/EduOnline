# PEP8规范  第一区域自带，第二区域第三方
# operation 用户相关操作

from datetime import datetime
from users.models import UserProfile
from course.models import Course

from django.db import models


# 用户咨询表
class UserAsk(models.Model):
    name = models.CharField('姓名', max_length=20)
    mobile = models.CharField('手机', max_length=11)
    course_name = models.CharField('课程名', max_length=50)
    add_time = models.DateTimeField('添加时间',auto_now_add=True)

    class Meta:
        verbose_name = '用户咨询'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


# 用户消息表
class UserMessage(models.Model):
    # user字段，默认0代表消息是发给所有用户；可以通过user.id发给特定用户消息
    user = models.IntegerField('接收用户', default=0)
    message = models.CharField('消息内容', max_length=500)
    has_read = models.BooleanField('是否已读', default=False)
    add_time = models.DateTimeField('添加时间',auto_now_add=True)

    class Meta:
        verbose_name = '用户消息'
        verbose_name_plural = verbose_name


# 课程评论表
class CourseComments(models.Model):
    user = models.ForeignKey(UserProfile, verbose_name='用户', on_delete=models.CASCADE)
    course = models.ForeignKey(Course, verbose_name='课程', on_delete=models.CASCADE)
    comments = models.CharField('评论', max_length=200)
    add_time = models.DateTimeField('添加时间',auto_now_add=True)

    class Meta:
        verbose_name = '课程评论'
        verbose_name_plural = verbose_name


# 用户已选课程表
class UserCourse(models.Model):
    user = models.ForeignKey(UserProfile, verbose_name='用户', on_delete=models.CASCADE)
    course = models.ForeignKey(Course, verbose_name='课程', on_delete=models.CASCADE)
    add_time = models.DateTimeField('添加时间',auto_now_add=True)

    class Meta:
        verbose_name = '用户已选课程'
        verbose_name_plural = verbose_name


# 用户收藏表
class UserFavorite(models.Model):
    fav_type_choices = (
        (1, '课程'),
        (2, '课程机构'),
        (3, '教师/讲师')
    )
    user = models.ForeignKey(UserProfile, verbose_name='用户', on_delete=models.CASCADE)
    fav_id = models.IntegerField('数据id', default=0)
    fav_type = models.IntegerField('收藏类型', choices=fav_type_choices, default=1)
    add_time = models.DateTimeField('添加时间',auto_now_add=True)

    class Meta:
        verbose_name = '用户收藏'
        verbose_name_plural = verbose_name