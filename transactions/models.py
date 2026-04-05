from decimal import Decimal
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone


class FinancialRecordQuerySet(models.QuerySet):
    def delete(self):
        """Perform a soft delete on a bulk queryset."""
        return self.update(is_deleted=True, deleted_at=timezone.now())

    def hard_delete(self):
        """Force delete on a bulk queryset."""
        return super().delete()

    def deleted(self):
        """Return only soft-deleted records."""
        return self.filter(is_deleted=True)

    def active(self):
        """Return only non-deleted records."""
        return self.filter(is_deleted=False)


class FinancialRecordManager(models.Manager):
    def get_queryset(self):
        return FinancialRecordQuerySet(self.model, using=self._db).active()

    def all_with_deleted(self):
        """Return all records, including soft-deleted ones."""
        return FinancialRecordQuerySet(self.model, using=self._db)

    def deleted_only(self):
        """Return only deleted records."""
        return FinancialRecordQuerySet(self.model, using=self._db).deleted()

    def active(self):
        """Proxy active() to QuerySet."""
        return self.get_queryset().active()


class FinancialRecord(models.Model):
    class RecordType(models.TextChoices):
        INCOME = "INCOME", "Income"
        EXPENSE = "EXPENSE", "Expense"

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"), message="Amount must be greater than zero.")],
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

    # Soft Delete fields
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    # Use the custom manager
    objects = FinancialRecordManager()

    class Meta:
        ordering = ["-date"]

    def __str__(self):
        return f"{self.type} | {self.category} | {self.amount} on {self.date}"

    def delete(self, using=None, keep_parents=False):
        """Override standard delete with soft delete."""
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save()

    def hard_delete(self, using=None, keep_parents=False):
        """Force a permanent delete from the database."""
        return super().delete(using=using, keep_parents=keep_parents)

    def restore(self):
        """Restore a soft-deleted record."""
        self.is_deleted = False
        self.deleted_at = None
        self.save()
