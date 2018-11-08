from __future__ import absolute_import
from celery import Celery
from django.conf import settings
import os

os.environ.setdefault('DJANGO_SETTING_MODULE', 'axf.settings')

app = Celery('mycelery')

# 设置时区
app.conf.CELERY_TIMEZONE = 'Asia/Shanghai'

# 将settings.py文件的配置加载过来
app.config_from_object('django.conf:settings')

# 设置自动发现任务  要求app的目录下有tasks.py文件
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)