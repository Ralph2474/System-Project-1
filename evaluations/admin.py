from django.contrib import admin

from .models import EvaluationRecord


@admin.register(EvaluationRecord)
class EvaluationRecordAdmin(admin.ModelAdmin):
    list_display = ('student', 'supervisor', 'rating')
