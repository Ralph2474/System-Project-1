from django.contrib import admin

from .models import DailyTimeLog


@admin.register(DailyTimeLog)
class DailyTimeLogAdmin(admin.ModelAdmin):
    list_display = ('student', 'entry_date', 'time_in', 'time_out')
