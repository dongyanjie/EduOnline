from django.urls import path, re_path

from .views import CourseListView, CourseDetailView, CourseLessonInfoView, CourseCommentView, AddCommentView, \
    VideoPlayView

app_name = 'course'

urlpatterns = [
    path('list/', CourseListView.as_view(), name='course_list'),
    # 课程详情
    re_path('course/(?P<course_id>\d+)/', CourseDetailView.as_view(), name='course_detail'),
    # 课程章节信息
    re_path('info/(?P<course_id>\d+)/', CourseLessonInfoView.as_view(), name='course_lesson_info'),
    # 课程评论
    re_path('comment/(?P<course_id>\d+)/', CourseCommentView.as_view(), name='course_comment'),
    # 添加评论
    path('add_comment/', AddCommentView.as_view(), name='add_comment'),
    # 课程视频播放页
    re_path('video/(?P<video_id>\d+)/', VideoPlayView.as_view(), name='video_play'),

]
