import xadmin

from .models import Course, Lesson, Video, CourseResource


# 在添加课程的时候添加课程资源,  inlines实现这一功能
class CourseResourceInline(object):
    model = CourseResource
    extra = 0


# xadmin继承自object
class CourseAdmin(object):
    # 课程

    # ######### get_zj_nums 直接使用函数名作为字段显示
    # list_display = ['name', 'desc', 'detail', 'degree', 'learn_times', 'students']
    list_display = ['course_org', 'teacher', 'name', 'desc', 'degree', 'learn_times', 'students', 'get_zj_nums']

    search_fields = ['course_org', 'name', 'desc', 'degree', 'students']
    list_filter = ['course_org', 'name', 'desc', 'degree', 'learn_times', 'students']

    # 增加课程资源, inlines实现这一功能
    inlines = [CourseResourceInline, ]

    # css,fonts在 ..\EduOnline\extra_apps\xadmin\static\xadmin\vendor\font-awesome 这个路径下
    # 查找图标网址 http://www.fontawesome.com.cn/
    model_icon = 'fa fa-book'  # 图标
    readonly_fields = ['click_nums']  # 只读字段，不能编辑

    # ordering = ['-click_nums']  # 排序
    # exclude = ['fav_nums']  # 不显示的字段
    # list_editable = ['degree', 'desc']  #在列表页可以直接编辑
    # refresh_times = [3, 5]  # 自动刷新（里面是秒数）

    # 当添加一门课程的时候，课程机构里面的课程数 +1
    def save_models(self):
        # 在保存课程的时候统计课程机构的课程数
        # obj实际是一个course对象
        obj = self.new_obj
        # 如果这里不保存，新增课程，统计的课程数会少一个
        obj.save()
        # 确定课程的课程机构存在。
        if obj.course_org is not None:
            # 找到添加的课程的课程机构
            course_org = obj.course_org
            # 课程机构的课程数量等于添加课程后的数量
            course_org.course_nums = Course.objects.filter(course_org=course_org).count()
            course_org.save()


class LessonAdmin(object):
    # 章节

    list_display = ['course', 'name', 'add_time']
    search_fields = ['course', 'name']
    # 这里course__name是根据课程名称过滤
    list_filter = ['course__name', 'name', 'add_time']


class VideoAdmin(object):
    # 视频

    list_display = ['lesson', 'name', 'add_time']
    search_fields = ['lesson', 'name']
    list_filter = ['lesson', 'name', 'add_time']


class CourseResourceAdmin(object):
    # 课程资源

    list_display = ['course', 'name', 'download', 'add_time']
    search_fields = ['course', 'name', 'download']
    list_filter = ['course__name', 'name', 'download', 'add_time']


# 注册关联
xadmin.site.register(Course, CourseAdmin)
xadmin.site.register(Lesson, LessonAdmin)
xadmin.site.register(Video, VideoAdmin)
xadmin.site.register(CourseResource, CourseResourceAdmin)
