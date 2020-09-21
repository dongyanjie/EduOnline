# # 后台全站的配置放在users\adminx.py中
import xadmin
from xadmin import views

from .models import EmailVerifyRecord, Banner


# CourseAdmin中使用详细
# css,fonts在 ..\EduOnline\extra_apps\xadmin\static\xadmin\vendor\font-awesome 这个路径下
# 查找图标网址 http://www.fontawesome.com.cn/
# model_icon = 'fa fa-book'  # 图标
# readonly_fields = ['click_nums']  # 只读字段，不能编辑
# ordering = ['-click_nums']  # 排序
# exclude = ['fav_nums']  # 不显示的字段
# list_editable = ['degree', 'desc']  #在列表页可以直接编辑
# refresh_times = [3, 5]  # 自动刷新（里面是秒数）


# # 创建xadmin的基本管理器配置，并与view绑定
# class BaseSetting(object):
#     # 开启主题功能
#     enable_themes = True
#     use_bootswatch = True
#
# # 将基本配置管理与view绑定
# xadmin.site.register(views.BaseAdminView, BaseSetting)


# 全局修改，固定写法
class GlobalSettings(object):
    # 修改title
    site_title = 'EduOnline后台管理系统'
    # 修改footer
    site_footer = 'EduOnline在线教育'
    # 收起菜单
    menu_style = 'accordion'


# 将title和footer信息进行注册
xadmin.site.register(views.CommAdminView, GlobalSettings)


# xadmin中这里是继承object，不再是继承admin
class EmailVerifyRecordAdmin(object):
    # 显示的字段
    list_display = ['code', 'email', 'send_type', 'send_time']
    # 搜索的字段，不要添加时间搜索
    search_fields = ['code', 'email', 'send_type']
    # 过滤的字段
    list_filter = ['code', 'email', 'send_type', 'send_time']


class BannerAdmin(object):
    list_display = ['title', 'images', 'url', 'index', 'add_time']
    search_fields = ['title', 'images', 'url', 'index']
    list_filter = ['title', 'images', 'url', 'index', 'add_time']


# 注册到后台
xadmin.site.register(EmailVerifyRecord, EmailVerifyRecordAdmin)
xadmin.site.register(Banner, BannerAdmin)
