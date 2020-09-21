# PEP8规范  第一区域自带，第二区域第三方
from datetime import datetime

from django.db import models


# 城市信息表
class CityDict(models.Model):
    name = models.CharField('城市', max_length=20)
    desc = models.CharField('描述', max_length=300, default='')
    add_time = models.DateTimeField('添加时间', auto_now_add=True)

    class Meta:
        verbose_name = '城市'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


# 课程机构信息表
class CourseOrg(models.Model):
    # 重新定义上传文件的路径
    def upload_to(self, filename):
        now_time = datetime.now().strftime("%Y%m")
        return '/'.join(['courseOrg', self.name, now_time, filename])

    org_choices = (
        ('pxjg', u"培训机构"),
        ('gx', u"高校"),
        ('gr', u"个人"),
    )
    # 机构所属类别
    category = models.CharField(verbose_name='机构类别', max_length=20, choices=org_choices, default='pxjg')

    name = models.CharField('机构名称', max_length=50)
    desc = models.TextField('机构描述', default='')
    fav_nums = models.IntegerField('收藏人数', default=0)
    click_nums = models.IntegerField('点击数', default=0)
    students = models.IntegerField("学习人数", default=0)
    course_nums = models.IntegerField("课程数", default=0)

    image = models.ImageField('封面图', upload_to=upload_to, max_length=100)
    address = models.CharField('机构地址', max_length=150)
    city = models.ForeignKey(CityDict, verbose_name='所在城市', on_delete=models.CASCADE)
    add_time = models.DateTimeField('添加时间', auto_now_add=True)
    tag = models.CharField('机构标签', max_length=20, default='全国知名')

    class Meta:
        verbose_name = '课程机构'
        verbose_name_plural = verbose_name

    def get_teacher_nums(self):
        # 获取机构的教师数(根据外键反向查询）
        # 反向查询  表名小写_set().all()
        return self.teacher_set.all().count()

    def __str__(self):
        return self.name


# 教师基本信息表
class Teacher(models.Model):
    # 重新定义上传文件的路径
    def upload_to(self, filename):
        filename = filename.split('.')[-2] + '_' + self.org.name + '.' + filename.split('.')[-1]
        return '/'.join(['courseOrg/teacherImage', filename])

    org = models.ForeignKey(CourseOrg, verbose_name='所属机构', on_delete=models.CASCADE)
    name = models.CharField('教师名', max_length=50)
    age = models.IntegerField('年龄', null=True, blank=True)
    work_years = models.IntegerField('工作年限', default=0)
    work_company = models.CharField('就职公司', max_length=50)
    work_position = models.CharField('公司职位', max_length=50)
    points = models.CharField('教学特点', max_length=200, default='')
    fav_nums = models.IntegerField('收藏人数', default=0)
    click_nums = models.IntegerField('点击数', default=0)
    add_time = models.DateTimeField('添加时间', auto_now_add=True)
    image = models.ImageField('头像', upload_to=upload_to, max_length=100, default='images/default.png')

    class Meta:
        verbose_name = '教师'
        verbose_name_plural = verbose_name

    # 获取讲师的课程数
    def get_course_nums(self):
        return self.course_set.all().count()

    def __str__(self):
        return '[{0}] 的教师: {1} '.format(self.org, self.name)
