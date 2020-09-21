from django.shortcuts import render, HttpResponse

from django.views.generic.base import View
from django.core.paginator import Paginator, EmptyPage, InvalidPage

from .models import Course, CourseOrg, CourseResource, Video
from operation.models import CourseComments, UserCourse, UserFavorite

from django.db.models import Q  # Q为使用并集查询(或操作)
from utils.mixin_utils import LoginRequiredMixin


class CourseListView(View):
    def get(self, request):
        all_courses = Course.objects.all().order_by('-add_time')
        # 热门课程推荐
        hot_courses = Course.objects.all().order_by('-click_nums')[:3]

        # 搜索功能
        search_keywords = request.GET.get('key_words', '')
        if search_keywords:
            # 在name字段进行操作,做like语句的操作。i代表不区分大小写
            # or操作使用Q
            all_courses = all_courses.filter(
                Q(name__icontains=search_keywords) | Q(desc__icontains=search_keywords) | Q(
                    detail__icontains=search_keywords))

        # 排序显示
        sort = request.GET.get('sort', '')
        if sort:
            if sort == 'students':
                all_courses = all_courses.order_by('-students')
            elif sort == 'hot':
                all_courses = all_courses.order_by('-click_nums')
        # 分页 每页显示3条
        paginator = Paginator(all_courses, 3)
        pages = paginator.page_range  # 生成所有页码
        num_page = paginator.num_pages  # 最大页数
        # 获取提交的页码
        page = request.GET.get('page', 1)
        try:
            courses = paginator.page(page)
        except (EmptyPage, InvalidPage):
            courses = paginator.page(1)

        return render(request, "course-list.html",
                      {'all_courses': courses, 'pages': pages, 'sort': sort, 'hot_courses': hot_courses})


# 课程详情
class CourseDetailView(View):
    def get(self, request, course_id):
        course = Course.objects.get(id=int(course_id))
        # 课程点击数加1
        course.click_nums += 1
        course.save()
        # 判断课程收藏和机构收藏
        has_fav_course = False
        has_fav_org = False
        # 必须用户已登录才能判断 fav_type=1代表收藏课程，fav_type=2代表收藏机构/高校
        if request.user.is_authenticated:
            if UserFavorite.objects.filter(user=request.user, fav_id=course_id, fav_type=1):
                has_fav_course = True
            if UserFavorite.objects.filter(user=request.user, fav_id=course.course_org.id, fav_type=2):
                has_fav_org = True

        # 通过当前标签查找数据库中的课程
        tag = course.tag
        if tag:
            # 相关课程推荐，推荐3个
            # exclude() 不等于，不包含
            # 查询id不等于当前课程id的 ，并且标签相同的三条数据
            related_courses = Course.objects.exclude(id=course_id).filter(tag=tag)[:3]
        else:
            related_courses = []
        return render(request, "course-detail.html",
                      {'course': course, 'related_courses': related_courses, 'has_fav_course': has_fav_course,
                       'has_fav_org': has_fav_org})


# 课程章节信息
class CourseLessonInfoView(View):
    def get(self, request, course_id):
        if not request.user.is_authenticated:
            # 未登录时返回json提示未登录
            return HttpResponse('{"status":"fail","msg":"用户未登录"}', content_type='application/json')

        course = Course.objects.get(id=int(course_id))
        # 课程学习数+1
        course.students += 1
        course.save()

        # 查询用户是否已经学习了该课程
        user_courses = UserCourse.objects.filter(user=request.user, course=course)
        if not user_courses:
            # 若没有学习，则把用户与课程关联起来
            user_course = UserCourse(user=request.user, course=course)
            user_course.save()

        # 相关课程推荐
        # 找到学习这门课的所有用户
        user_courses = UserCourse.objects.filter(course=course)
        # 找到学习这门课的所有用户的id
        user_ids = [user_course.user_id for user_course in user_courses]
        # 通过所有用户id，找到所有用户学习过的课程
        all_user_courses = UserCourse.objects.filter(user_id__in=user_ids)
        # 取出所有课程id
        course_ids = [all_user_course.course_id for all_user_course in all_user_courses]
        # 通过所有课程id找到所有课程，按点击量取前3个
        related_courses = Course.objects.filter(id__in=course_ids).order_by('-click_nums')[:3]

        # 获取当前课程的课程资源
        all_resources = CourseResource.objects.filter(course=course)

        return render(request, 'course-video.html',
                      {'course': course, 'all_resources': all_resources, 'related_courses': related_courses})


# 课程评论
class CourseCommentView(View):
    def get(self, request, course_id):
        course = Course.objects.get(id=int(course_id))
        all_resources = CourseResource.objects.filter(course=course)
        all_comments = CourseComments.objects.filter(course=course)

        return render(request, "course-comment.html", {
            "course": course, "all_resources": all_resources, 'all_comments': all_comments,
        })


# 添加评论
class AddCommentView(View):
    def post(self, request):
        if not request.user.is_authenticated:
            # 未登录时返回json提示未登录
            return HttpResponse('{"status":"fail","msg":"用户未登录"}', content_type='application/json')
        course_id = request.POST.get("course_id", 0)
        comments = request.POST.get('comments', '')
        if int(course_id) > 0 and comments:
            # 实例化一个course_comment对象
            course_comments = CourseComments()
            # 获取评论的是哪门课程
            course = Course.objects.get(id=int(course_id))
            # 分别把评论的课程、评论的内容和评论的用户保存到数据库
            course_comments.course = course
            course_comments.comments = comments
            course_comments.user = request.user
            course_comments.save()
            return HttpResponse('{"status":"success", "msg":"评论成功"}', content_type='application/json')
        else:
            return HttpResponse('{"status":"fail", "msg":"评论失败"}', content_type='application/json')


# 视频章节视频播放页(继承LoginRequiredMixin基类，若用户未登录则跳转到登录页)
class VideoPlayView(LoginRequiredMixin, View):
    def get(self, request, video_id):
        video = Video.objects.get(id=int(video_id))
        # 通过外键找到章节再找到视频对应的课程
        course = video.lesson.course
        course.students += 1
        course.save()
        # 查询用户是否已经学习该课程
        user_courses = UserCourse.objects.filter(user=request.user, course=course)
        if not user_courses:
            # 若没有学习，则把该课程与用户关联起来
            user_course = UserCourse(user=request.user, course=course)
            user_course.save()

        # 相关课程推荐
        # 找到学习这门课的所有用户
        user_courses = UserCourse.objects.filter(course=course)
        # 找到学习这门课的所有用户的id
        user_ids = [user_course.user_id for user_course in user_courses]
        # 通过所有用户的id,找到所有用户学习过的所有过程
        all_user_courses = UserCourse.objects.filter(user_id__in=user_ids)
        # 取出所有课程id
        course_ids = [all_user_course.course_id for all_user_course in all_user_courses]
        # 通过所有课程的id,找到所有的课程，按点击量去五个
        relate_courses = Course.objects.filter(id__in=course_ids).order_by("-click_nums")[:5]

        # 资源
        all_resources = CourseResource.objects.filter(course=course)
        return render(request, 'course-play.html', {
            'course': course, 'all_resources': all_resources,
            'relate_courses': relate_courses, 'video': video,
        })


def teacher_list(request):
    pass


def org_list(request):
    pass
