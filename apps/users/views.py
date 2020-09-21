from django.shortcuts import render, reverse, HttpResponse, HttpResponseRedirect, render_to_response
from django.contrib.auth import authenticate, login, logout  # 验证,登录,注销

from django.contrib.auth.backends import ModelBackend  # 模型基类
from django.contrib.auth.hashers import make_password  # 密码加密

from django.db.models import Q  # Q为使用并集查询(或操作)
from django.views.generic.base import View  # 基于类形式写接口

from .models import UserProfile, EmailVerifyRecord, Banner
from .forms import LoginForm, RegisterForm, ForgetPwdForm, ModifyPwdForm, UploadImageForm, UserInfoForm
from operation.models import UserCourse, UserFavorite, UserMessage
from course.models import Course, CourseOrg
from organization.models import Teacher

from utils.email_send import send_register_email  # 发送邮件接口
from django.core.paginator import Paginator, EmptyPage, InvalidPage  # django内置分页

from utils.mixin_utils import LoginRequiredMixin
import logging
import json


# ONLINE首页
class IndexView(View):
    def get(self, request):
        # 轮播图
        all_banners = Banner.objects.all().order_by('-add_time')[:4]
        # 课程
        courses = Course.objects.filter(is_banner=False)[:6]
        # 轮播课程
        banner_courses = Course.objects.filter(is_banner=True)[:3]
        # 课程机构
        course_orgs = Course.objects.all()[:6]
        return render(request, 'index.html', {
            'all_banners': all_banners,
            'courses': courses,
            'banner_courses': banner_courses,
            'course_orgs': course_orgs,
        })


# 邮箱名和用户名都可以登录
# 定制后端类--继承ModelBackend类,重写authenticate方法
class CustomBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            # 不希望用户存在两个，get只能有一个。两个是get失败的一种原因 Q为使用并集查询
            user = UserProfile.objects.get(Q(username=username) | Q(email=username))

            # django后台中密码加密:
            # UserProfile继承AbstractUser中有def check_password(self, raw_password):
            if user.check_password(password):
                return user

        except Exception as e:
            logging.info(e)


# 登录页(基于类形式,继承View类)
class LoginView(View):
    # 说明：
    # 如果是get请求，直接返回登录页面给用户
    # 如果是post请求，先生成一个表单实例，并获取用户提交的所有信息（request.POST）
    # is_valid()方法，验证用户的提交信息是不是合法
    # 如果合法，获取用户提交的username和password
    # 将用户提交的数据与数据库对比
    # 若验证通过,则跳转到edu首页,并将用户信息记录在cookie中
    # 若验证不一致,则返回登录页,并提示错误信息

    def get(self, request):
        return render(request, 'login.html')

    def post(self, request):
        # 实例化表单
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            # 获取用户提交的用户名和密码
            user_name = request.POST.get('username', None)
            pass_word = request.POST.get('password', None)

            # 成功返回user对象,失败返回None
            user = authenticate(username=user_name, password=pass_word)
            # 如果不是null说明验证成功
            if user is not None:
                # 只有激活后才能登录
                if user.is_active:
                    # 登录
                    login(request, user)
                    return HttpResponseRedirect(reverse('users:index'))
                else:
                    return render(request, 'login.html', {'msg': '当前账号未注册,请注册成功后再登录', 'login_form': login_form})
            else:
                return render(request, 'login.html', {'msg': '用户名或密码错误', 'login_form': login_form})
        # 当验证不通过
        else:
            return render(request, 'login.html', {'login_form': login_form})


# 退出登录
class LogoutView(View):
    def get(self, request):
        logout(request)
        # 退出登录需要重定向
        from django.urls import reverse
        return HttpResponseRedirect(reverse('users:index'))


# 主要实现功能:
# 用户输入邮箱、密码和验证码，点注册按钮
# 如果输入的不正确，提示错误信息
# 如果正确，发送激活邮件，用户通过邮件激活后才能登陆
# 即使注册成功，没有激活的用户也不能登陆


# 用户注册页(基于类形式,继承View类)
class RegisterView(View):
    # 说明：
    # 如果是get请求，直接返回注册页面给用户
    # 如果是post请求，先生成一个表单实例，并获取用户提交的所有信息（request.POST）
    # is_valid()方法，验证用户的提交信息是不是合法
    # 如果合法，获取用户提交的email和password
    # 实例化一个user_profile对象，把用户添加到数据库
    # 默认添加的用户是激活状态（is_active=1表示True），在这里我们修改默认的状态（改为is_active = False），只有用户去邮箱激活之后才改为True
    # 对密码加密，然后保存，发送邮箱，username是用户注册的邮箱，‘register’表明是注册
    # 注册成功跳转到登录界面

    def get(self, request):
        register_form = RegisterForm()
        return render(request, 'register.html', {'register_form': register_form})

    def post(self, request):
        register_form = RegisterForm(request.POST)
        if register_form.is_valid():
            email = request.POST.get('email', None)
            # 如有用户已存在,则提示错误信息
            if UserProfile.objects.filter(email=email):
                return render(request, 'register.html', {'register_form': register_form, 'msg': '该邮箱已注册,请直接登录'})
            pass_word = request.POST.get('password', None)
            # 实例化一个user_profile对象
            user_obj = UserProfile()
            user_obj.username = email
            user_obj.email = email
            # 默认注册用户未激活,需要到邮箱中激活才能登录
            user_obj.is_active = False
            # 对保存到数据库的密码加密
            user_obj.password = make_password(pass_word)
            user_obj.save()
            # 提交后发送激活邮件给用户
            send_register_email(email, 'register')
            return render(request, 'send_success.html', {'msg': '注册成功，请到邮箱里激活后登录'})
            # return render(request, 'login.html', {'msg': '注册成功，请到邮箱里激活后登录'})
        else:
            return render(request, 'register.html', {'register_form': register_form})


# 激活用户(通过邮箱)
class ActiveUserView(View):
    # 说明:
    # 根据邮箱找到对应的用户，然后设置is_active = True来实现

    def get(self, request, active_code):
        # 查询邮箱验证记录是否存在
        curr_record = EmailVerifyRecord.objects.filter(code=active_code)
        # 若存在
        if curr_record:
            for record in curr_record:
                # 获取对应邮箱
                email = record.email
                # 查找邮箱对应的user
                user = UserProfile.objects.get(email=email)
                # 激活用户
                user.is_active = True
                user.save()
        # 若验证码不对,则跳转到激活失败页面
        else:
            return render(request, "active_fail.html", {'msg': '非常抱歉,链接已失效,请重试...'})
        # 激活成功跳转到登录页面
        return render(request, 'login.html', {'msg': '恭喜您,激活成功'})


# 找回密码页
class ForgetPwdView(View):
    # 说明：
    # 用户点“忘记密码”，跳到找回密码页面
    # 在forgetpwd页面，输入邮箱和验证码成功后，发送邮件提醒
    # 通过点击邮件链接，可以重置密码
    # 两次密码输的正确无误后，密码更新成功，跳到登录界面

    def get(self, request):
        forget_form = ForgetPwdForm()
        return render(request, 'forgetpwd.html', {'forget_form': forget_form})

    def post(self, request):
        forget_form = ForgetPwdForm(request.POST)
        if forget_form.is_valid():
            email = request.POST.get('email', None)

            # 如有用户不存在, 则提示错误信息
            if not UserProfile.objects.filter(email=email):
                return render(request, 'forgetpwd.html', {'forget_form': forget_form, 'msg': '该账户不存在，请先注册'})

            # 确认后发送 找回密码邮件给用户
            send_register_email(email, 'forget')
            return render(request, 'send_success.html', {'msg': '邮件已发送,请到邮件地址内继续下一步操作'})
        else:
            return render(request, 'forgetpwd.html', {'forget_form': forget_form})


# 重置密码页(get方式)
class ResetView(View):
    def get(self, request, active_code):
        # 根据code到数据库中查询是否存在
        curr_record = EmailVerifyRecord.objects.filter(code=active_code)
        if curr_record:
            for record in curr_record:
                email = record.email
                # 携带该邮箱信息转到密码重置页
                return render(request, "password_reset.html", {"email": email})
        else:
            return render(request, "active_fail.html", {'msg': '非常抱歉,链接已失效,请重试...'})
        return render(request, 'login.html')


# 修改密码后台逻辑
class ModifyPwdView(View):
    def post(self, request):
        # 获取表单提交数据
        modify_form = ModifyPwdForm(request.POST)
        # 校验
        if modify_form.is_valid():
            pwd1 = request.POST.get('password1', None)
            pwd2 = request.POST.get('password2', None)
            email = request.POST.get('email', None)
            if pwd1 != pwd2:
                return render(request, 'password_reset.html',
                              {'email': email, 'modify_form': modify_form, 'msg': '两次密码输入不一致'})
            user = UserProfile.objects.get(email=email)
            user.password = make_password(pwd2)
            user.save()

            # return redirect(reverse("users:user_login"), {'msg': '密码修改成功，可以登录啦'})
            return render(request, 'send_success.html', {'msg': '密码修改成功，可以登录啦'})
        else:
            email = request.POST.get('email', None)
            return render(request, 'password_reset.html', {'email': email, 'modify_form': modify_form})


# 用户个人信息页(装饰器，必须登录才能进入该页面，否则跳转到登录页)
class UserInfoView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'userCenter-info.html')

    def post(self, request):
        user_info_form = UserInfoForm(request.POST)
        if user_info_form.is_valid():
            user_info_form.save()
            return HttpResponse('{"status":"success"}', content_type='application/json')
        else:
            return HttpResponse(json.dumps(user_info_form.errors), content_type='application/json')


# 用户头像修改
class UploadImageView(LoginRequiredMixin, View):
    def post(self, request):
        # 上传文件都在request.FILES里面获取
        image_form = UploadImageForm(request.POST, request.FILES)
        # 验证数据
        if image_form.is_valid():
            # 获取数据
            image = image_form.cleaned_data['image']
            request.user.image = image
            request.user.save()
            return HttpResponse('{"status":"success"}', content_type='application/json')
        else:
            return HttpResponse('{"status":"fail"}', content_type='application/json')


# 修改用户密码
class UpdatePwdView(LoginRequiredMixin, View):
    def post(self, request):
        modify_form = ModifyPwdForm(request.POST)
        if modify_form.is_valid():
            pwd1 = request.POST.get('password1', '')
            pwd2 = request.POST.get('password2', '')
            if pwd1 != pwd2:
                return HttpResponse('{"status":"fail","msg":"密码不一致"}', content_type='application/json')
            user = request.user
            user.password = make_password(pwd2)
            user.save()

            return HttpResponse('{"status":"success","msg":"修改成功"}', content_type='application/json')
        else:
            # 返回表单定义的错误(json格式)
            return HttpResponse(json.dumps(modify_form.errors), content_type='application/json')


# 发送邮箱修改验证码
class SendEmailCodeView(LoginRequiredMixin, View):
    def get(self, request):
        email = request.GET.get('email', '')

        if UserProfile.objects.filter(email=email):
            return HttpResponse('{"status":"fail","msg":"该邮箱已存在,请更换"}', content_type='application/json')

        # 发送邮箱验证码
        send_register_email(email, 'update_email')
        return HttpResponse('{"status":"success"}', content_type='application/json')


# 修改邮箱
class UpdateEmailView(LoginRequiredMixin, View):
    def post(self, request):
        email = request.POST.get('email', '')
        code = request.POST.get('code', '')
        # 查询当前修改是否存在
        existed_records = EmailVerifyRecord.objects.filter(email=email, code=code, send_type='update_email')
        if existed_records:
            user = request.user
            user.email = email
            user.save()
            return HttpResponse('{"status":"success","msg":"修改成功"}', content_type='application/json')
        else:
            return HttpResponse('{"status":"fail","msg":"验证码无效"}', content_type='application/json')


# 我的课程
class MyCourseView(LoginRequiredMixin, View):
    def get(self, request):
        user_courses = UserCourse.objects.filter(user=request.user)
        return render(request, "userCenter-mycourse.html", {
            "user_courses": user_courses,
        })


# 我的收藏-课程
class MyFavCourseView(LoginRequiredMixin, View):
    # fav_type=1代表课程 fav_type=2代表机构 fav_type=3代表讲师
    def get(self, request):
        course_list = []
        fav_courses = UserFavorite.objects.filter(user=request.user, fav_type=1)
        for fav_course in fav_courses:
            course_id = fav_course.fav_id
            course = Course.objects.get(id=course_id)
            course_list.append(course)
        return render(request, 'userCenter-fav-course.html', {"course_list": course_list, })


# 我的收藏-课程机构
class MyFavOrgView(LoginRequiredMixin, View):

    def get(self, request):
        org_list = []
        fav_orgs = UserFavorite.objects.filter(user=request.user, fav_type=2)
        for fav_org in fav_orgs:
            # 取出fav_id 也就是机构id
            org_id = fav_org.fav_id
            # 获取机构信息
            org = CourseOrg.objects.get(id=org_id)
            # 追加到列表中
            org_list.append(org)
        return render(request, "userCenter-fav-org.html", {"org_list": org_list, })


# 我的收藏-授课讲师
class MyFavTeacherView(LoginRequiredMixin, View):
    def get(self, request):
        teacher_list = []
        fav_teachers = UserFavorite.objects.filter(user=request.user, fav_type=3)
        for fav_teacher in fav_teachers:
            teacher_id = fav_teacher.fav_id
            teacher = Teacher.objects.get(id=teacher_id)
            teacher_list.append(teacher)
        return render(request, "userCenter-fav-teacher.html", {"teacher_list": teacher_list, })


# 我的消息
class MyMessageView(LoginRequiredMixin, View):
    def get(self, request):
        # 消息表对应user.id
        all_message = UserMessage.objects.filter(user=request.user.id)

        # 分页
        p = Paginator(all_message, 6)
        pages = p.page_range  # 生成所有页码
        page_nums = p.num_pages  # 最大页码
        # 用户输入的页码
        page = request.GET.get('page', 1)
        try:
            messages = p.page(page)
        except (InvalidPage, EmptyPage):
            messages = p.page(1)
        return render(request, "userCenter-message.html", {"messages": messages, 'pages': pages})


# 全局404页面
def page_not_found(request):
    response = render_to_response('404.html', {})
    response.status_code = 404
    return response


# 全局500页面
def page_error(request):
    response = render_to_response('500.html', {})
    response.status_code = 500
    return response
