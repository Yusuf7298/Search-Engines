from celery import Celery
app = Celery('test')
print("Celery works!")
