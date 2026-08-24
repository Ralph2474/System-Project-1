from django.conf import settings
from django.db import models

from internships.models import InternshipPosting


class ApplicationRecord(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_APPROVED = 'approved'
    STATUS_REJECTED = 'rejected'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_APPROVED, 'Approved'),
        (STATUS_REJECTED, 'Rejected'),
    ]

    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='applications')
    internship = models.ForeignKey(InternshipPosting, on_delete=models.CASCADE, related_name='applications')
    cover_letter = models.TextField(blank=True)
    applied_on = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    decision_note = models.TextField(blank=True, default='')

    class Meta:
        ordering = ['-applied_on']
        unique_together = ('student', 'internship')

    def __str__(self):
        return f"{self.student.username} -> {self.internship.title}"


class PlacementRecord(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='placements')
    internship = models.ForeignKey(InternshipPosting, on_delete=models.CASCADE, related_name='placements')
    company_supervisor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='supervised_placements')
    placement_date = models.DateField(blank=True, null=True)

    class Meta:
        unique_together = ('student', 'internship')

    def __str__(self):
        return f"Placement: {self.student.username} @ {self.internship.title}"
