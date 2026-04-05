from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.db import models


class FinancialRecord(models.Model):
    class RecordType(models.TextChoices):
        INCOME = "INCOME", "Income"
        EXPENSE = "EXPENSE", "Expense"

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0.01, message="Amount must be greater than zero.")],
    )
    type = models.CharField(max_length=7, choices=RecordType.choices)
    category = models.CharField(max_length=100)
    date = models.DateField()
    description = models.TextField(blank=True, default="")
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="financial_records",
    )

    class Meta:
        ordering = ["-date"]

    def __str__(self):
        return f"{self.type} | {self.category} | {self.amount} on {self.date}"
