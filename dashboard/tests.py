from datetime import date
from decimal import Decimal

from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from transactions.models import FinancialRecord
from users.models import Profile


class DashboardAnalyticsTests(APITestCase):
    def setUp(self):
        # Create user
        self.user = User.objects.create_user(username="testuser", password="password")
        Profile.objects.create(user=self.user, role=Profile.Role.VIEWER)
        
        # Create mock transactions
        FinancialRecord.objects.create(
            amount=Decimal("1000.00"),
            type=FinancialRecord.RecordType.INCOME,
            category="Salary",
            date=date.today(),
            created_by=self.user,
        )
        FinancialRecord.objects.create(
            amount=Decimal("200.00"),
            type=FinancialRecord.RecordType.EXPENSE,
            category="Food",
            date=date.today(),
            created_by=self.user,
        )
        FinancialRecord.objects.create(
            amount=Decimal("150.00"),
            type=FinancialRecord.RecordType.EXPENSE,
            category="Transport",
            date=date.today(),
            description="Bus fare",
            created_by=self.user,
        )

        self.summary_url = reverse("dashboard:summary")
        self.client.force_authenticate(user=self.user)

    def test_dashboard_summary_totals(self):
        """Verify the total income, expenses, and net balance aggregation."""
        response = self.client.get(self.summary_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        totals = response.data["totals"]
        self.assertEqual(Decimal(str(totals["total_income"])), Decimal("1000.00"))
        self.assertEqual(Decimal(str(totals["total_expenses"])), Decimal("350.00"))
        self.assertEqual(Decimal(str(totals["net_balance"])), Decimal("650.00"))

    def test_dashboard_category_distribution(self):
        """Verify the totals per category."""
        response = self.client.get(self.summary_url)
        dist = response.data["category_distribution"]
        
        # Salary: 1000, Food: 200, Transport: 150
        categories = {item["category"]: Decimal(str(item["total"])) for item in dist}
        self.assertEqual(categories["Salary"], Decimal("1000.00"))
        self.assertEqual(categories["Food"], Decimal("200.00"))
        self.assertEqual(categories["Transport"], Decimal("150.00"))

    def test_dashboard_recent_activity_limit(self):
        """Verify that recent activity respects the limit."""
        recent_url = reverse("dashboard:recent")
        # Add 10 more transactions
        for i in range(10):
            FinancialRecord.objects.create(
                amount=Decimal("10.00"),
                type=FinancialRecord.RecordType.INCOME,
                category="Misc",
                date=date.today(),
                created_by=self.user,
            )
        
        # Test default (5)
        response = self.client.get(recent_url)
        self.assertEqual(len(response.data), 5)
        
        # Test explicit limit (10)
        response = self.client.get(f"{recent_url}?limit=10")
        self.assertEqual(len(response.data), 10)
        
        # Test max limit (50)
        response = self.client.get(f"{recent_url}?limit=100")
        self.assertEqual(len(response.data), 13) # Total 13 (3 initial + 10 additional)
