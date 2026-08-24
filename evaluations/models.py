from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from decimal import Decimal


class EvaluationRecord(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='student_evaluations')
    supervisor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='supervisor_evaluations')
    rating = models.PositiveSmallIntegerField(default=0)
    comments = models.TextField(blank=True)
    punctuality = models.PositiveSmallIntegerField(default=0)
    professionalism = models.PositiveSmallIntegerField(default=0)
    teamwork = models.PositiveSmallIntegerField(default=0)
    submitted_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-submitted_on']
        unique_together = ('student', 'supervisor')

    def clean(self):
        # Prevent self-evaluation. Compare the raw FK ids rather than the
        # related objects: the supervisor is often assigned by the view
        # after the form is validated (it isn't a form field), so
        # self.supervisor may not be resolvable yet and accessing it would
        # raise RelatedObjectDoesNotExist instead of a clean validation error.
        if self.student_id and self.supervisor_id and self.student_id == self.supervisor_id:
            raise ValidationError("A supervisor cannot evaluate themselves.")

        # Validate rating ranges
        if self.rating < 1 or self.rating > 5:
            raise ValidationError({'rating': 'Rating must be between 1 and 5.'})

        if self.punctuality < 1 or self.punctuality > 5:
            raise ValidationError({'punctuality': 'Punctuality rating must be between 1 and 5.'})

        if self.professionalism < 1 or self.professionalism > 5:
            raise ValidationError({'professionalism': 'Professionalism rating must be between 1 and 5.'})

        if self.teamwork < 1 or self.teamwork > 5:
            raise ValidationError({'teamwork': 'Teamwork rating must be between 1 and 5.'})

    @property
    def average_score(self):
        return (
            Decimal(self.rating + self.punctuality + self.professionalism + self.teamwork) / Decimal('4')
        ).quantize(Decimal('0.01'))

    @property
    def score_percent(self):
        return (self.average_score / Decimal('5') * Decimal('100')).quantize(Decimal('0.01'))

    @property
    def grade(self):
        if self.score_percent >= 90:
            return 'A'
        if self.score_percent >= 80:
            return 'B'
        if self.score_percent >= 70:
            return 'C'
        if self.score_percent >= 60:
            return 'D'
        return 'F'

    def __str__(self):
        return f"Evaluation for {self.student.username}"