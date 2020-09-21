from django.urls import path, include, re_path
from . import views
from users.views import IndexView, LoginView, LogoutView, RegisterView, ForgetPwdView, ModifyPwdView, UserInfoView, \
    UploadImageView, UpdatePwdView, SendEmailCodeView, UpdateEmailView, MyCourseView, MyFavCourseView, MyFavOrgView, \
    MyFavTeacherView, MyMessageView

app_name = 'users'

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('login/', LoginView.as_view(), name='user_login'),
    path('logout/', LogoutView.as_view(), name='user_logout'),

    path('register/', RegisterView.as_view(), name='user_register'),
    # 激活邮箱的url
    path('forgetpwd/', ForgetPwdView.as_view(), name='user_forgetpwd'),
    # 修改密码url
    path('modifypwd', ModifyPwdView.as_view(), name='user_modifypwd'),
    # 用户信息页
    path('info/', UserInfoView.as_view(), name='user_info'),
    # 修改用户头像页
    path('image/upload/', UploadImageView.as_view(), name='image_upload'),
    # 修改用户密码
    path('update/pwd/', UpdatePwdView.as_view(), name='update_pwd'),
    # 发送邮箱验证码
    path('sendemail_code/', SendEmailCodeView.as_view(), name='sendemail_code'),
    # 修改邮箱
    path('update_email/', UpdateEmailView.as_view(), name='update_email'),
    # 我的课程
    path("mycourse/", MyCourseView.as_view(), name='mycourse'),
    # 我的消息
    path('my_message/', MyMessageView.as_view(), name="my_message"),
    # 我的收藏--课程
    path('myfav/course/', MyFavCourseView.as_view(), name="myfav_course"),
    # 我的收藏--课程机构/高校
    path('myfav/org/', MyFavOrgView.as_view(), name="myfav_org"),
    # 我的收藏--授课讲师
    path('myfav/teacher/', MyFavTeacherView.as_view(), name="myfav_teacher"),

]
