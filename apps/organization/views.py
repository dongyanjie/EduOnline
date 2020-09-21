from django.shortcuts import render, HttpResponse
from django.views.generic.base import View

from .models import CourseOrg, CityDict, Teacher
from operation.models import UserFavorite
from course.models import Course

from .forms import UserAskForm
from django.db.models import Q  # Q为使用并集查询(或操作)

# 分页组件
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage


# 分页第三方库
# from pure_pagination import Paginator, EmptyPage, PageNotAnInteger


# 课程机构
class OrgView(View):
    def get(self, request):
        # 取出所有课程
        all_orgs = CourseOrg.objects.all()
        # 取出所有城市
        all_citys = CityDict.objects.all()

        # 机构搜索功能
        search_keywords = request.GET.get('keywords', '')
        if search_keywords:
            # 在name字段进行操作,做like语句的操作。i代表不区分大小写
            # or操作使用Q
            all_orgs = all_orgs.filter(Q(name__icontains=search_keywords) | Q(desc__icontains=search_keywords))

        # 进行城市与分类的联动:
        # 当选择全部类别的时候，就只通过当前城市id。
        # 当选择全部城市的时候，就只通过当前目录id。
        # 当两者都选的时候使用&连接

        # 城市筛选
        city_id = request.GET.get('city', '')
        if city_id:
            all_orgs = all_orgs.filter(city_id=int(city_id))
        # 类别筛选
        category = request.GET.get('ct', '')
        if category:
            all_orgs = all_orgs.filter(category=category)

        # 热门课程机构排名
        hot_orgs = all_orgs.order_by('-click_nums')[:3]

        # 学习人数和课程数筛选
        sort = request.GET.get('sort', '')
        if sort:
            if sort == 'students':
                all_orgs = all_orgs.order_by('-students')
            elif sort == 'courses':
                all_orgs = all_orgs.order_by('-course_nums')

        # 有多少家机构（先筛选再统计数量）
        org_nums = all_orgs.count()

        # 对课程机构分页显示:  从all_orgs中取出，每页显示3条数据
        paginator = Paginator(all_orgs, 3)
        pages = paginator.page_range  # 生成所有页码
        num_page = paginator.num_pages  # 最大页码
        # 获取前台get请求page参数，默认第一页
        page = request.GET.get('page', 1)
        try:
            orgs = paginator.page(page)  # 调用指定页面的内容
        except PageNotAnInteger:
            # 如果输入页码小于1，则显示第一页
            orgs = paginator.page(1)
        except EmptyPage:
            # 如果输入页码超出最后一页码，则显示最后一页
            orgs = paginator.page(num_page)

        return render(request, 'org-list.html',
                      {'all_orgs': orgs, 'all_citys': all_citys, 'org_nums': org_nums, 'pages': pages,
                       'city_id': city_id, 'category': category, 'sort': sort, 'hot_orgs': hot_orgs})


# 用户添加咨询
class AddAskView(View):
    def post(self, request):
        userask_form = UserAskForm(request.POST)
        if userask_form.is_valid():
            # 保存到数据库
            user_ask = userask_form.save(commit=True)
            # 如果保存成功,返回json字符串,后面content type是告诉浏览器返回的数据类型
            return HttpResponse('{"status":"success","msg":"提交成功"}', content_type='application/json')
        else:
            # 如果保存失败，返回json字符串,并将form的报错信息通过msg传递到前端
            return HttpResponse('{"status":"fail","msg":"提交失败"}', content_type='application/json')


# 进入指定机构首页
class OrgHomeView(View):
    def get(self, request, org_id):
        current_page = 'home'

        # 根据org_id 找到课程机构
        course_org = CourseOrg.objects.get(id=int(org_id))
        # 机构/高校 的点击数加1
        course_org.click_nums += 1
        course_org.save()

        # 判断收藏状态
        has_fav = False
        if request.user.is_authenticated:
            if UserFavorite.objects.filter(user=request.user, fav_id=course_org.id, fav_type=2):
                has_fav = True
        # 反向查询课程机构的所有课程和老师
        all_courses = course_org.course_set.all()[:4]
        all_teacher = course_org.teacher_set.all()[:2]
        return render(request, 'org-detail-homepage.html',
                      {'course_org': course_org, 'all_courses': all_courses, 'all_teacher': all_teacher,
                       'current_page': current_page, 'has_fav': has_fav})


# 机构讲师页
class OrgTeacherView(View):
    def get(self, request, org_id):
        current_page = 'teacher'

        # 根据id取到课程机构
        course_org = CourseOrg.objects.get(id=int(org_id))
        # 反向查询课程机构的所有老师
        all_teacher = course_org.teacher_set.all()
        # 判断收藏状态
        has_fav = False
        if request.user.is_authenticated:
            if UserFavorite.objects.filter(user=request.user, fav_id=course_org.id, fav_type=2):
                has_fav = True
        return render(request, 'org-detail-teachers.html', {
            'course_org': course_org,
            'all_teacher': all_teacher,
            'current_page': current_page,
            'has_fav': has_fav
        })


# 机构讲师列表
class TeacherListView(View):
    def get(self, request):
        all_teachers = Teacher.objects.all()
        # 总共有多少老师
        teacher_nums = all_teachers.count()

        # 搜索功能
        search_keywords = request.GET.get('keywords', '')
        if search_keywords:
            # 在name字段进行操作,做like语句的操作。i代表不区分大小写
            # or操作使用Q
            all_teachers = all_teachers.filter(name__icontains=search_keywords)

        # 教师人气排行
        sort = request.GET.get('sort', '')
        if sort:
            if sort == 'hot':
                all_teachers = all_teachers.order_by('-click_nums')
        # 教师排行榜
        sorted_teacher = Teacher.objects.all().order_by('-click_nums')[:3]

        # 分页
        p = Paginator(all_teachers, 6)
        pages = p.page_range  # 生成所有页数
        page_nums = p.num_pages  # 最大页数
        # 获取用户输入页数
        page = request.GET.get('page', 1)
        try:
            teachers = p.page(page)
        except PageNotAnInteger:
            teachers = p.page(1)
        except EmptyPage:
            teachers = p.page(page_nums)

        return render(request, 'teachers-list.html',
                      {'all_teachers': teachers, 'teacher_nums': teacher_nums, 'pages': pages,
                       'sorted_teacher': sorted_teacher, 'sort': sort})


# 机构讲师详情
class TeacherDetailView(View):
    def get(self, request, teacher_id):
        teacher = Teacher.objects.get(id=int(teacher_id))
        # 教师点击数加1
        teacher.click_nums += 1
        teacher.save()

        # 获取该讲师的所有课程
        all_courses = Course.objects.filter(teacher=teacher)
        # 判断收藏状态(fav_type=1表示收藏喜欢的课程，fav_type=2表示收藏喜欢的机构/高校，fav_type=3表示收藏喜欢的教师）
        has_teacher_fav = False
        has_org_fav = False
        if request.user.is_authenticated:
            if UserFavorite.objects.filter(user=request.user, fav_id=teacher.id, fav_type=3):
                has_teacher_fav = True
            if UserFavorite.objects.filter(user=request.user, fav_id=teacher.org.id, fav_type=2):
                has_org_fav = True

        # 讲师排行榜
        sorted_teacher = Teacher.objects.all().order_by('-click_nums')[:3]
        return render(request, 'teacher-detail.html',
                      {'teacher': teacher, 'all_courses': all_courses, 'sorted_teacher': sorted_teacher,
                       'has_teacher_fav': has_teacher_fav, 'has_org_fav': has_org_fav})


# 机构课程列表页
class OrgCourseView(View):
    def get(self, request, org_id):
        current_page = 'course'
        # 根据id取到课程机构
        course_org = CourseOrg.objects.get(id=int(org_id))
        # 通过课程机构找到课程。内建的变量，找到指向这个字段的外键引用
        all_courses = course_org.course_set.all()
        # 判断收藏状态
        has_fav = False
        if request.user.is_authenticated:
            if UserFavorite.objects.filter(user=request.user, fav_id=course_org.id, fav_type=2):
                has_fav = True

        return render(request, 'org-detail-course.html', {
            'course_org': course_org, 'all_courses': all_courses, 'current_page': current_page, 'has_fav': has_fav
        })


# 机构课程详情
class CourseDetailView(View):
    def get(self, request):
        pass


# 机构详细介绍页
class OrgDescView(View):
    def get(self, request, org_id):
        current_page = 'desc'
        course_org = CourseOrg.objects.get(id=int(org_id))
        # 判断收藏状态
        has_fav = False
        if request.user.is_authenticated:
            if UserFavorite.objects.filter(user=request.user, fav_id=course_org.id, fav_type=2):
                has_fav = True
        return render(request, 'org-detail-desc.html', {
            'course_org': course_org, 'current_page': current_page, 'has_fav': has_fav
        })


# 用户收藏和取消收藏
class OrgAddFavView(View):
    def post(self, request):
        id = request.POST.get('fav_id', 0)  # 防止后边int(fav_id)时出错
        type = request.POST.get('fav_type', 0)  # 防止int(fav_type)出错

        if not request.user.is_authenticated:
            # 未登录时返回json提示未登录，跳转到登录页面是在ajax中做的
            return HttpResponse('{"status":"fail","msg":"用户未登录"}', content_type='application/json')
        exist_record = UserFavorite.objects.filter(user=request.user, fav_id=int(id), fav_type=int(type))
        if exist_record:
            # 如果记录已经存在，表示用户取消收藏
            exist_record.delete()
            if int(type) == 1:
                course = Course.objects.get(id=int(id))
                course.fav_nums -= 1
                if course.fav_nums < 0:
                    course.fav_nums = 0
                course.save()
            elif int(type) == 2:
                org = CourseOrg.objects.get(id=int(id))
                org.fav_nums -= 1
                if org.fav_nums < 0:
                    org.fav_nums = 0
                org.save()
            elif int(type) == 3:
                teacher = Teacher.objects.get(id=int(id))
                teacher.fav_nums -= 1
                if teacher.fav_nums < 0:
                    teacher.fav_nums = 0
                teacher.save()

            return HttpResponse('{"status":"success","msg":"收藏"}', content_type='application/json')
        else:
            # 若记录不存在，表示用户收藏
            user_fav = UserFavorite()
            if int(id) > 0 and int(type) > 0:
                user_fav.user = request.user
                user_fav.fav_id = int(id)
                user_fav.fav_type = int(type)
                user_fav.save()

                if int(type) == 1:
                    course = Course.objects.get(id=int(id))
                    course.fav_nums += 1
                    course.save()
                elif int(type) == 2:
                    org = CourseOrg.objects.get(id=int(id))
                    org.fav_nums += 1
                    org.save()
                elif int(type) == 3:
                    teacher = Teacher.objects.get(id=int(id))
                    teacher.fav_nums += 1
                    teacher.save()

                return HttpResponse('{"status":"success", "msg":"已收藏"}', content_type='application/json')
            else:
                return HttpResponse('{"status":"fail", "msg":"收藏出错"}', content_type='application/json')
