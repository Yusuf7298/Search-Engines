import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'IR_Search_Engines.settings')

app = Celery('IR_Search_Engines')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()