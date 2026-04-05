from datetime import date
from decimal import Decimal

from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import FinancialRecord
from users.models import Profile


class FinancialRecordTests(APITestCase):
    def setUp(self):
        # Create users with different roles
        self.admin_user = User.objects.create_user(username="admin", password="password")
        Profile.objects.create(user=self.admin_user, role=Profile.Role.ADMIN)

        self.analyst_user = User.objects.create_user(username="analyst", password="password")
        Profile.objects.create(user=self.analyst_user, role=Profile.Role.ANALYST)

        self.viewer_user = User.objects.create_user(username="viewer", password="password")
        Profile.objects.create(user=self.viewer_user, role=Profile.Role.VIEWER)

        self.record_url = reverse("transactions:financial-record-list")
        
        # Initial data
        self.record = FinancialRecord.objects.create(
            amount=Decimal("500.00"),
            type=FinancialRecord.RecordType.INCOME,
            category="Salary",
            date=date.today(),
            created_by=self.admin_user,
        )
        self.detail_url = reverse("transactions:financial-record-detail", kwargs={"pk": self.record.pk})

    def test_admin_full_access(self):
        """Admin should have full CRUD access."""
        self.client.force_authenticate(user=self.admin_user)
        
        # 1. READ
        response = self.client.get(self.record_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 2. CREATE
        data = {
            "amount": "100.50",
            "type": FinancialRecord.RecordType.EXPENSE,
            "category": "Food",
            "date": str(date.today()),
        }
        response = self.client.post(self.record_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # 3. UPDATE
        response = self.client.patch(self.detail_url, {"amount": "600.00"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 4. DELETE
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_analyst_read_only_access(self):
        """Analyst should be able to read but not write."""
        self.client.force_authenticate(user=self.analyst_user)
        
        # 1. READ
        response = self.client.get(self.record_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 2. CREATE
        response = self.client.post(self.record_url, {"amount": "100.00"})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # 3. DELETE
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_viewer_no_access(self):
        """Viewer role (lowest) should not have access to financial records CRUD."""
        self.client.force_authenticate(user=self.viewer_user)
        
        # 1. READ
        response = self.client.get(self.record_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_amount_validation(self):
        """Verify that negative amounts are rejected."""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post(self.record_url, {"amount": "-10.00", "type": "INCOME", "category": "Test", "date": str(date.today())})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("amount", response.data)
