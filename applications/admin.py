from django.contrib import admin

from .models import ApplicationRecord, PlacementRecord


@admin.register(ApplicationRecord)
class ApplicationRecordAdmin(admin.ModelAdmin):
    list_display = ('student', 'internship', 'status')


@admin.register(PlacementRecord)
class PlacementRecordAdmin(admin.ModelAdmin):
    list_display = ('student', 'internship', 'company_supervisor')
