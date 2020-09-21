# from django.contrib import admin
import xadmin

from django.views.static import serve
from django.urls import path, re_path, include

# from EduOnline.settings import MEDIA_ROOT, STATIC_ROOT
from EduOnline.settings import MEDIA_ROOT
from users.views import IndexView, ActiveUserView, ResetView, LoginView

urlpatterns = [
    # 设置一个url处理静态文件(在debug=false情况下生效)
    # re_path(r'^static/(?P<path>.*)', serve, {'document_root': STATIC_ROOT}),

    # path('admin/', admin.site.urls),
    # 使用xadmin后台
    path('xadmin/', xadmin.site.urls),

    path('', IndexView.as_view()),  # 默认显示首页
    path('index/', IndexView.as_view()),  # 默认显示首页
    path('login/', LoginView.as_view()),  # 登录页

    path('users/', include('users.urls', namespace="users")),
    path('course/', include('course.urls', namespace="course")),
    path('org/', include('organization.urls', namespace="organization")),

    # 富文本编辑器url(未实现)
    path('ueditor/', include('DjangoUeditor.urls')),
    # 第三方验证码库
    path('captcha/', include('captcha.urls')),
    # 邮件激活的url
    re_path('active/(?P<active_code>.*)/', ActiveUserView.as_view(), name='user_active'),
    # 邮件重置密码url
    re_path('reset/(?P<active_code>.*)/', ResetView.as_view(), name='user_reset'),

    # 处理图片显示的url,使用Django自带serve,传入参数告诉它去哪个路径找，
    re_path(r'media/(?P<path>.*)', serve, {'document_root': MEDIA_ROOT}),

]

# 只有设置debug=False时生效
# 全局404页码配置
handler404 = 'users.views.page_not_found'
# 全局500页码配置
handler500 = 'users.views.page_error'
