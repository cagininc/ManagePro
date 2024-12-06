from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')  # Django settings'inizi doğru gösterin

app = Celery('backend')

# Django settings'ini Celery'ye tanıtmak için config_from_object 
app.config_from_object('django.conf:settings', namespace='CELERY')

# Otomatik olarak tüm registered task'leri bulup Celery'ye ekler
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
