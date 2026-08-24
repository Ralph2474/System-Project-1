from django.conf import settings
from django.db import models
from django.utils import timezone


class CompanyPosting(models.Model):
    name = models.CharField(max_length=150)
    contact_email = models.EmailField(blank=True)
    description = models.TextField(blank=True)
    linked_profile = models.OneToOneField(
        'accounts.CompanyProfile',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='posting_company',
        help_text='Company account (self-registered via /register/) this posting record represents, if any.',
    )

    def __str__(self):
        return self.name

    @property
    def is_self_registered(self):
        return self.linked_profile_id is not None


class InternshipPosting(models.Model):
    company = models.ForeignKey(CompanyPosting, on_delete=models.CASCADE, related_name='postings')
    title = models.CharField(max_length=200)
    location = models.CharField(max_length=120, blank=True)
    duration = models.CharField(max_length=80, blank=True)
    description = models.TextField(blank=True)
    required_hours = models.PositiveIntegerField(default=120)
    slots_available = models.PositiveIntegerField(default=1)
    deadline = models.DateField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_postings')
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-deadline', '-updated_at']

    def __str__(self):
        return self.title

    @property
    def is_open(self):
        today = timezone.localdate()
        has_slots = self.slots_available > 0
        not_expired = self.deadline is None or self.deadline >= today
        return self.is_active and has_slots and not_expired
