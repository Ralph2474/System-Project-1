from django.urls import path

from .views import company_create, internship_create, internship_delete, internship_detail, internship_list, internship_report, internship_update

app_name = 'internships'

urlpatterns = [
    path('', internship_list, name='posting_list'),
    path('report.xlsx', internship_report, name='posting_report'),
    path('create/', internship_create, name='posting_create'),
    path('<int:pk>/edit/', internship_update, name='posting_update'),
    path('<int:pk>/delete/', internship_delete, name='posting_delete'),
    path('company/create/', company_create, name='company_create'),
    path('<int:pk>/', internship_detail, name='posting_detail'),
]
