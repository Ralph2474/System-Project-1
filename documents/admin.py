from django.contrib import admin

from .models import SubmittedDocument


@admin.register(SubmittedDocument)
class SubmittedDocumentAdmin(admin.ModelAdmin):
    list_display = ('student', 'document_type', 'status')
