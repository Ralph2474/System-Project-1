from django.contrib import admin

from .models import CompanyPosting, InternshipPosting


@admin.register(CompanyPosting)
class CompanyPostingAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact_email', 'is_self_registered', 'linked_profile')


@admin.register(InternshipPosting)
class InternshipPostingAdmin(admin.ModelAdmin):
    list_display = ('title', 'company', 'location', 'required_hours', 'slots_available', 'deadline', 'is_active')
