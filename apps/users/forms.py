from django import forms
from django.core.exceptions import ValidationError
from users.models import UserProfile

# 引入第三方验证码库
from captcha.fields import CaptchaField


# 登录表单验证
class LoginForm(forms.Form):
    username = forms.CharField(required=True, error_messages={'required': '用户名不能为空'})
    password = forms.CharField(required=True, min_length=5,
                               error_messages={'required': '密码不能为空', 'min_length': u'密码至少5位'})


# 注册表单验证
class RegisterForm(forms.Form):
    email = forms.EmailField(required=True, error_messages={'required': '请输入正确的邮箱'})
    password = forms.CharField(required=True, min_length=5,
                               error_messages={'required': '密码不能为空', 'min_length': u'密码至少5位'})

    # 验证码,字段里自定义错误提示信息
    captcha = CaptchaField(error_messages={'invalid': '验证码错误'})


# 找回密码表单验证
class ForgetPwdForm(forms.Form):
    email = forms.EmailField(required=True, error_messages={'required': '请输入正确的邮箱'})
    # 验证码,字段里自定义错误提示信息
    captcha = CaptchaField(error_messages={'invalid': '验证码错误'})


# 重置密码表单
class ModifyPwdForm(forms.Form):
    password1 = forms.CharField(required=True, min_length=5,
                                error_messages={'required': '密码不能为空', 'min_length': u'密码至少5位'})
    password2 = forms.CharField(required=True, min_length=5,
                                error_messages={'required': '密码不能为空', 'min_length': u'密码至少5位'})

    # 自定义方法（全局钩子, 检验两个字段），检验两次密码一致;
    def clean(self):
        if self.cleaned_data.get('password1') != self.cleaned_data.get('password2'):
            raise ValidationError('两次密码输入不一致')
        else:
            return self.cleaned_data


# 用户头像修改表单
class UploadImageForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['image']


# 个人中心信息修改表单
class UserInfoForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['nick_name', 'gender', 'birthday', 'mobile', 'address']
