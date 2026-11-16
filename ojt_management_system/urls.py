"""
URL configuration for ojt_management_system project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('accounts.urls', namespace='accounts')),
    path('dashboard/', include('dashboard.urls', namespace='dashboard')),
    path('activity-log/', include('auditlog.urls', namespace='auditlog')),
    path('internships/', include('internships.urls', namespace='internships')),
    path('applications/', include('applications.urls', namespace='applications')),
    path('timelog/', include('timelog.urls', namespace='timelog')),
    path('documents/', include('documents.urls', namespace='documents')),
    path('evaluations/', include('evaluations.urls', namespace='evaluations')),
]

# Uploaded documents are NOT exposed under a public /media/ URL. They are served
# by documents:document_file, which checks that the viewer is the owning
# student or a coordinator (and works with DEBUG=False).
