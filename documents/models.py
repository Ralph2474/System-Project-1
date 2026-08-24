from django.conf import settings
from django.db import models


class SubmittedDocument(models.Model):
    DOCUMENT_MOA = 'moa'
    DOCUMENT_WAIVER = 'waiver'
    DOCUMENT_RESUME = 'resume'
    DOCUMENT_WEEKLY_REPORT = 'weekly_report'
    DOCUMENT_CHOICES = [
        (DOCUMENT_MOA, 'MOA'),
        (DOCUMENT_WAIVER, 'Waiver'),
        (DOCUMENT_RESUME, 'Resume'),
        (DOCUMENT_WEEKLY_REPORT, 'Weekly Report'),
    ]

    STATUS_PENDING = 'pending'
    STATUS_VALIDATED = 'validated'
    STATUS_REJECTED = 'rejected'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_VALIDATED, 'Validated'),
        (STATUS_REJECTED, 'Rejected'),
    ]

    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='documents')
    document_type = models.CharField(max_length=20, choices=DOCUMENT_CHOICES)
    file = models.FileField(upload_to='documents/')
    uploaded_on = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    validation_note = models.TextField(blank=True, default='')

    class Meta:
        ordering = ['-uploaded_on']

    def __str__(self):
        return f"{self.student.username} - {self.document_type}"
