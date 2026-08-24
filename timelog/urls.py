from django.urls import path

from .views import time_log_delete, time_log_form, time_log_list, time_log_update

app_name = 'timelog'

urlpatterns = [
    path('', time_log_list, name='time_log_list'),
    path('new/', time_log_form, name='time_log_form'),
    path('<int:pk>/edit/', time_log_update, name='time_log_update'),
    path('<int:pk>/delete/', time_log_delete, name='time_log_delete'),
]
