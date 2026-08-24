from django.test import TestCase

from .forms import RegistrationForm
from .models import CompanyProfile, CustomUser, StudentProfile


class RegistrationTests(TestCase):
    def test_public_registration_excludes_coordinator_role(self):
        role_values = [value for value, label in RegistrationForm().fields['role'].choices]
        self.assertEqual(role_values, [CustomUser.ROLE_STUDENT, CustomUser.ROLE_COMPANY_SUPERVISOR])

    def test_student_registration_creates_student_profile(self):
        response = self.client.post('/register/', {
            'username': 'newstudent',
            'email': 'student@example.com',
            'role': CustomUser.ROLE_STUDENT,
            'student_number': 'ST-001',
            'course': 'Computer Science',
            'department': 'Computing',
            'password1': 'StrongStudentPass123!',
            'password2': 'StrongStudentPass123!',
        })

        self.assertRedirects(response, '/dashboard/')
        user = CustomUser.objects.get(username='newstudent')
        self.assertEqual(user.role, CustomUser.ROLE_STUDENT)
        self.assertEqual(user.student_profile.student_number, 'ST-001')

    def test_company_registration_requires_company_details(self):
        form = RegistrationForm(data={
            'username': 'companyuser',
            'email': 'company@example.com',
            'role': CustomUser.ROLE_COMPANY_SUPERVISOR,
            'password1': 'StrongCompanyPass123!',
            'password2': 'StrongCompanyPass123!',
        })

        self.assertFalse(form.is_valid())
        self.assertIn('company_name', form.errors)
        self.assertIn('contact_person', form.errors)
