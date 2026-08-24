from django.urls import path

from .views import (application_decide, application_list, application_manage,
                    application_withdraw, apply_to_internship, placement_update)

app_name = 'applications'

urlpatterns = [
    path('', application_list, name='application_list'),
    path('apply/<int:pk>/', apply_to_internship, name='apply_to_internship'),
    path('<int:pk>/withdraw/', application_withdraw, name='application_withdraw'),
    path('manage/', application_manage, name='application_manage'),
    path('placement/<int:pk>/update/', placement_update, name='placement_update'),
    path('manage/<int:pk>/decide/', application_decide, name='application_decide'),
]
