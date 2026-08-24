from django.test import TestCase

from accounts.models import CustomUser
from applications.models import ApplicationRecord

from .models import CompanyPosting, InternshipPosting


class InternshipWorkflowTests(TestCase):
    def setUp(self):
        self.student = CustomUser.objects.create_user(
            username='student', password='StudentPass123!', role=CustomUser.ROLE_STUDENT
        )
        self.coordinator = CustomUser.objects.create_user(
            username='coordinator', password='CoordinatorPass123!', role=CustomUser.ROLE_COORDINATOR
        )
        self.company = CompanyPosting.objects.create(name='Partner Company')
        self.posting = InternshipPosting.objects.create(
            company=self.company,
            title='Software Intern',
            required_hours=120,
            slots_available=2,
        )

    def test_student_can_browse_but_cannot_export_report(self):
        self.client.force_login(self.student)
        self.assertEqual(self.client.get('/internships/').status_code, 200)
        self.assertEqual(self.client.get('/internships/report.xlsx').status_code, 403)

    def test_coordinator_can_export_excel_report(self):
        self.client.force_login(self.coordinator)
        response = self.client.get('/internships/report.xlsx')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response['Content-Type'],
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        )

    def test_posting_with_application_cannot_be_deleted(self):
        ApplicationRecord.objects.create(
            student=self.student,
            internship=self.posting,
            cover_letter='Interested in this role.',
        )
        self.client.force_login(self.coordinator)
        response = self.client.post(f'/internships/{self.posting.pk}/delete/')

        self.assertRedirects(response, f'/internships/{self.posting.pk}/')
        self.assertTrue(InternshipPosting.objects.filter(pk=self.posting.pk).exists())
