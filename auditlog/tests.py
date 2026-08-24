from django.test import TestCase

from accounts.models import CustomUser

from .models import AuditLog


class AuditLogTests(TestCase):
    def test_authenticated_dashboard_request_creates_audit_record(self):
        user = CustomUser.objects.create_user(
            username='student', password='StudentPass123!', role=CustomUser.ROLE_STUDENT
        )
        self.client.force_login(user)

        response = self.client.get('/dashboard/')

        self.assertEqual(response.status_code, 200)
        self.assertTrue(AuditLog.objects.filter(user=user, path='/dashboard/').exists())
