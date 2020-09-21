# PEP8规范  第一区域自带，第二区域第三方
from datetime import datetime

from django.db import models

from organization.models import CourseOrg, Teacher

from EduOnline.settings import MEDIA_ROOT


# 课程信息表
class Course(models.Model):
    # 重新定义上传文件的路径
    def upload_to(self, filename):
        filename = filename.split('.')[-2] + '_' + str(datetime.now().strftime("%Y%m%d%H%M%S")) + '.' + \
                   filename.split('.')[-1]
        return '/'.join(['course/coverArt', self.name, filename])

    degree_choices = (
        ('cj', '初级'),
        ('zj', '中级'),
        ('gj', '高级')
    )
    # 课程所属机构
    course_org = models.ForeignKey(CourseOrg, on_delete=models.CASCADE, verbose_name="所属机构", null=True, blank=True)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, verbose_name='讲师/教授', null=True, blank=True)
    #  “课程须知”和“老师告诉你能学到什么”
    youneed_know = models.CharField('课程须知', max_length=300, default='课程须知:')
    teacher_tell = models.CharField('老师告诉你', max_length=300, default='...')

    name = models.CharField('课程名', max_length=50)
    desc = models.CharField('课程描述', max_length=300)
    detail = models.TextField('课程详情', default='')
    degree = models.CharField('难度', choices=degree_choices, max_length=10)
    learn_times = models.IntegerField('学习时长(分钟数)', default=0)
    students = models.IntegerField('学习人数', default=0)
    fav_nums = models.IntegerField('收藏人数', default=0)
    click_nums = models.IntegerField('点击数', default=0)
    image = models.ImageField('封面图', upload_to=upload_to, max_length=100)
    add_time = models.DateTimeField('添加时间', auto_now_add=True)

    tag = models.CharField('课程标签', max_length=10, default='')
    category = models.CharField('课程类别', max_length=20, default='')
    is_banner = models.BooleanField('是否轮播', default=False)

    class Meta:
        verbose_name = '课程信息'
        verbose_name_plural = verbose_name

    def get_zj_nums(self):
        # 获取课程章节数， 根据外键反向查询
        # 反向查询 ： 表名小写_set().all()
        return self.lesson_set.all().count()

    # 在后台显示的名称,使后台课程列表多了“章节数”字段
    get_zj_nums.short_description = '章节数'

    def get_course_lesson(self):
        # 获取课程的章节
        return self.lesson_set.all()

    def get_learn_users(self):
        # 获取课程的学习用户
        return self.usercourse_set.all()[:5]

    def __str__(self):
        return self.name


# 章节信息表
class Lesson(models.Model):
    # 课程 章节  一对多   级联删除
    course = models.ForeignKey(Course, verbose_name='课程', on_delete=models.CASCADE)
    name = models.CharField('章节名', max_length=100)
    add_time = models.DateTimeField('添加时间', auto_now_add=True)

    class Meta:
        verbose_name = '章节信息'
        verbose_name_plural = verbose_name

    def get_lesson_video(self):
        # 获取章节视频
        return self.video_set.all()

    def __str__(self):
        return '<{0}> 课程的章节 >>> {1} '.format(self.course, self.name)


# 视频信息表
class Video(models.Model):
    # 重新定义上传文件的路径
    def upload_to(self, filename):
        return '/'.join(['course/video', self.lesson.course, self.lesson, filename])

    # 章节 视频 一对多   级联删除
    lesson = models.ForeignKey(Lesson, verbose_name='章节', on_delete=models.CASCADE)
    name = models.CharField('视频名', max_length=100)
    video = models.FileField('视频', upload_to=upload_to, null=True, blank=True)

    url = models.CharField('视频链接/访问地址', max_length=200, default='')
    learn_times = models.IntegerField("学习时长(分钟数)", default=0)
    add_time = models.DateTimeField('添加时间', auto_now_add=True)

    class Meta:
        verbose_name = '视频'
        verbose_name_plural = verbose_name


# 课程资源表
class CourseResource(models.Model):
    # 重新定义上传文件的路径
    def upload_to(self, filename):
        filename = filename.split('.')[-2] + '_' + str(datetime.now().strftime("%Y%m%d%H%M%S")) + '.' + \
                   filename.split('.')[-1]
        return '/'.join(['course/resource', self.course.name, filename])

    # 课程资源 课程  一对多   级联删除
    course = models.ForeignKey(Course, verbose_name="课程", on_delete=models.CASCADE)
    name = models.CharField('资源名', max_length=100)
    download = models.FileField("资源文件", upload_to=upload_to, max_length=200)
    add_time = models.DateTimeField('添加时间', auto_now_add=True)

    class Meta:
        verbose_name = "课程资源"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name
