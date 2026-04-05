import django_filters

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
