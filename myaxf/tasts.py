from celery import task
# 要有url, html页面, send_mail, 缓存: key(uuid) value(user_id)
from django.conf import settings
from django.core.cache import caches
from django.core.mail import send_mail
from django.template import loader

# 获得缓存
cache = caches['confirm']

@task
def send_verify_mail(url, user_id, reciver, uuid_str):
    title = '第一会所sis001'
    content = ''
    template = loader.get_template('user/email.html')
    # 渲染
    html = template.render({'url': url})
    # 收件人
    email_from = settings.DEFAULT_FROM_EMAIL
    # 发送邮件
    send_mail(title, content, email_from, [reciver], html_message=html)
    # 设置缓存
    cache.set(uuid_str, user_id, settings.VERIFY_CODE_MAX_AGE)