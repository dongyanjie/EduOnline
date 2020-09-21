from django.urls import path, re_path
from organization.views import OrgView, TeacherListView, AddAskView, OrgHomeView, OrgCourseView, OrgTeacherView, \
    OrgDescView, OrgAddFavView, TeacherDetailView,CourseDetailView

app_name = 'org'
urlpatterns = [
    # 机构列表
    path('list/', OrgView.as_view(), name='org_list'),
    # 讲师列表
    re_path('teacher/list/', TeacherListView.as_view(), name='teacher_list'),
    # 讲师详情
    re_path('teacher/detail/(?P<teacher_id>\d+)/', TeacherDetailView.as_view(), name="teacher_detail"),
    # 课程详情
    re_path('course/detail/(?P<course_id>\d+)/', CourseDetailView.as_view(), name="course_detail"),
    # path('teacher/detail/<int:org_id>/', TeacherDetailView.as_view(), name="teacher_detail"),

    # 用户咨询
    path('add-ask/', AddAskView.as_view(), name='add_ask'),
    # 指定机构首页
    re_path('home/(?P<org_id>\d+)/', OrgHomeView.as_view(), name='org_home'),
    # 机构讲师页
    re_path('teacher/(?P<org_id>\d+)/', OrgTeacherView.as_view(), name='org_teacher'),
    # 机构课程页
    re_path('course/(?P<org_id>\d+)/', OrgCourseView.as_view(), name='org_course'),
    # 机构详情描述页
    re_path('desc/(?P<org_id>\d+)/', OrgDescView.as_view(), name='org_desc'),

    # 机构收藏
    path('add_fav/', OrgAddFavView.as_view(), name='add_fav'),
]
