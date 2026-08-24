from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    ROLE_STUDENT = 'student'
    ROLE_COORDINATOR = 'coordinator'
    ROLE_COMPANY_SUPERVISOR = 'company_supervisor'

    ROLE_CHOICES = [
        (ROLE_STUDENT, 'Student'),
        (ROLE_COORDINATOR, 'Coordinator'),
        (ROLE_COMPANY_SUPERVISOR, 'Company Supervisor'),
    ]

    role = models.CharField(max_length=32, choices=ROLE_CHOICES, default=ROLE_STUDENT)

    def __str__(self):
        return self.get_username()


class StudentProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='student_profile')
    student_number = models.CharField(max_length=50, blank=True)
    course = models.CharField(max_length=120, blank=True)
    department = models.CharField(max_length=120, blank=True)

    def __str__(self):
        return f"{self.user.username} profile"


class CompanyProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='company_profile')
    company_name = models.CharField(max_length=150, blank=True)
    contact_person = models.CharField(max_length=120, blank=True)
    office_address = models.CharField(max_length=250, blank=True)

    def __str__(self):
        return f"{self.company_name or self.user.username}"
