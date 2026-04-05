import django_filters
from rest_framework.exceptions import ValidationError

from .models import FinancialRecord


class FinancialRecordFilter(django_filters.FilterSet):
    # date range: ?date_after=2024-01-01&date_before=2024-12-31
    date_after = django_filters.DateFilter(field_name="date", lookup_expr="gte")
    date_before = django_filters.DateFilter(field_name="date", lookup_expr="lte")

    class Meta:
        model = FinancialRecord
        fields = {
            "category": ["exact"],
            "type": ["exact"],
        }

    def filter_queryset(self, queryset):
        """Add cross-field validation: date_after must not be after date_before."""
        date_after = self.form.cleaned_data.get("date_after")
        date_before = self.form.cleaned_data.get("date_before")

        if date_after and date_before and date_after > date_before:
            raise ValidationError(
                {"date_after": "date_after must not be later than date_before."}
            )

        return super().filter_queryset(queryset)
