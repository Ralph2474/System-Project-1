from django.urls import path

from .views import evaluation_delete, evaluation_detail, evaluation_form, evaluation_list

app_name = 'evaluations'

urlpatterns = [
    path('', evaluation_list, name='evaluation_list'),
    path('submit/', evaluation_form, name='evaluation_form'),
    path('submit/<int:student_id>/', evaluation_form, name='evaluation_form_for_student'),
    path('<int:pk>/', evaluation_detail, name='evaluation_detail'),
    path('<int:pk>/delete/', evaluation_delete, name='evaluation_delete'),
]
