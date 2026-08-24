from django.conf import settings
from django.db import models
from django.utils import timezone


class DailyTimeLog(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='time_logs')
    entry_date = models.DateField()
    time_in = models.TimeField(blank=True, null=True)
    time_out = models.TimeField(blank=True, null=True)
    accomplishment = models.TextField(blank=True)
    hours_completed = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    REQUIRED_HOURS = 500  # Default required hours for OJT completion

    class Meta:
        ordering = ['-entry_date']
        unique_together = ('student', 'entry_date')

    def __str__(self):
        return f"{self.student.username} - {self.entry_date}"

    @classmethod
    def get_student_hours(cls, student):
        """Calculate total hours completed by a student."""
        return cls.objects.filter(student=student).aggregate(
            total=models.Sum('hours_completed')
        )['total'] or 0

    @classmethod
    def get_student_progress(cls, student):
        """Calculate student's progress percentage towards required hours."""
        total_hours = cls.get_student_hours(student)
        progress = (total_hours / cls.REQUIRED_HOURS) * 100 if cls.REQUIRED_HOURS > 0 else 0
        return min(progress, 100)  # Cap at 100%

    @classmethod
    def get_remaining_hours(cls, student):
        """Calculate remaining hours for a student."""
        total_hours = cls.get_student_hours(student)
        remaining = cls.REQUIRED_HOURS - total_hours
        return max(remaining, 0)  # Don't show negative hours