from django.contrib import admin

from .models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'user', 'action', 'method', 'path', 'status_code', 'ip_address')
    list_filter = ('action', 'method', 'status_code', 'created_at')
    search_fields = ('user__username', 'path', 'details', 'ip_address')
    readonly_fields = ('user', 'action', 'method', 'path', 'status_code', 'ip_address', 'details', 'created_at')
    date_hierarchy = 'created_at'
