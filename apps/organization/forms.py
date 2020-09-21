import re
from django import forms
from operation.models import UserAsk


# 咨询页表单
# class UserAskForm(forms.Form):
class UserAskForm(forms.ModelForm):
    class Meta:
        model = UserAsk
        fields = ['name', 'mobile', 'course_name']

    # 验证手机号码是否合法
    def clean_mobile(self):
        mobile = self.cleaned_data['mobile']
        # regex_moblie="^1[358]\d{9}$|^147\d{8}$|176\d{8}$"
        regex_mobile = "^1\d{10}$"
        #  构建正则规则
        p = re.compile(regex_mobile)
        if p.match(mobile):
            return mobile
        else:
            raise forms.ValidationError(u"手机号码非法", code="mobile_invalid")
