from django.urls import path

from .views import document_decide, document_delete, document_list, document_upload, document_validate

app_name = 'documents'

urlpatterns = [
    path('', document_list, name='document_list'),
    path('upload/', document_upload, name='document_upload'),
    path('<int:pk>/delete/', document_delete, name='document_delete'),
    path('validate/', document_validate, name='document_validate'),
    path('validate/<int:pk>/', document_decide, name='document_decide'),
]
