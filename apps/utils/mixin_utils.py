# apps/utils/mixin_utils.py

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator


# 如果是用函数方式写的话直接加个装饰器（@login_required）就可以;用类方式写，必须用继承
# 在django中已Mixin结尾的，就代表最基本的View
class LoginRequiredMixin(object):
    @method_decorator(login_required(login_url='/login/'))
    def dispatch(self, request, *args, **kwargs):
        return super(LoginRequiredMixin, self).dispatch(request, *args, **kwargs)
