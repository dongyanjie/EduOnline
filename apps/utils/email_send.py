# email_send.py
import logging
from random import Random  # 随机数库
from django.core.mail import send_mail  # 内置smtp邮件发送模块

from users.models import EmailVerifyRecord
# 发件人(发邮件账号)
from EduOnline.settings import EMAIL_FROM


# 生成随机字符串,默认6位
def random_str(random_length=6):
    str = ''
    # 可选字符串
    chars = 'AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz0123456789'
    length = len(chars) - 1
    random = Random()
    for i in range(random_length):
        str += chars[random.randint(0, length)]
    return str


# 发送注册邮件
def send_register_email(email, send_type="register"):
    # 实例化一个EmailVerifyRecord对象
    email_record = EmailVerifyRecord()
    # 生成随机code放入链接中
    if send_type == 'update_email':
        code = random_str(4)
    else:
        code = random_str(16)

    email_record.code = code
    email_record.email = email
    email_record.send_type = send_type
    # 发送之前先保存到数据库,到时候查询链接是否存在
    email_record.save()

    # 定义邮件内容
    email_title = ""
    email_body = ""

    if send_type == "register":
        email_title = "EduOnline注册激活链接"
        email_body = "[EduOnline] 请点击下面的链接激活你的账号:<a href='http://127.0.0.1:8000/active/{0}'>http://127.0.0.1:8000/active/{1}</a>".format(code,code)

        # 使用Django内置函数发送邮件--官方文档
        # def send_mail(subject, message, from_email, recipient_list,
        #               fail_silently=False, auth_user=None, auth_password=None,
        #               connection=None, html_message=None):
        # 四个参数：主题，邮件内容，发件人邮箱地址，收件人（是一个字符串列表）
        send_status = send_mail(email_title, email_body, EMAIL_FROM, [email])
        # 如果发送成功
        if send_status:
            logging.info(email, '激活邮件发送成功，注意查收--')

    if send_type == "forget":
        email_title = "EduOnline找回密码链接"
        email_body = "[EduOnline] 请点击下面的链接找回你的密码: <a href='http://127.0.0.1:8000/reset/{0}'>http://127.0.0.1:8000/reset/{1}</a>".format(code,code)

        # 四个参数：主题，邮件内容，从哪里发，接受者list
        send_status = send_mail(email_title, email_body, EMAIL_FROM, [email])
        # 如果发送成功
        if send_status:
            logging.info(email, '找回密码邮件发送成功，注意查收--')

    if send_type == "update_email":
        email_title = "邮箱修改验证码"
        email_body = "[EduOnline] 您的邮箱验证码为{0}，5分钟内有效，请勿泄露。".format(code)

        send_status = send_mail(email_title, email_body, EMAIL_FROM, [email])
        if send_status:
            pass
