from django.urls import path

from .views import activity_log

app_name = 'auditlog'

urlpatterns = [
    path('', activity_log, name='activity_log'),
]
