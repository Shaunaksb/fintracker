from datetime import date
from dateutil.relativedelta import relativedelta

from django.db.models import Sum, Count
from django.db.models.functions import TruncMonth, TruncWeek

from transactions.models import FinancialRecord


class FinanceAnalytics:
    """
    Pure service class — no HTTP logic here.
    All calculations are pushed down to the database via .aggregate()
    and .annotate() for maximum PostgreSQL efficiency.
    """

    # ------------------------------------------------------------------
    # Totals
    # ------------------------------------------------------------------
    @staticmethod
    def get_totals() -> dict:
        """Returns total income, total expenses, and net balance."""
        result = FinancialRecord.objects.aggregate(
            total_income=Sum(
                "amount",
                filter=__import__("django.db.models", fromlist=["Q"]).Q(type=FinancialRecord.RecordType.INCOME),
                default=0,
            ),
            total_expenses=Sum(
                "amount",
                filter=__import__("django.db.models", fromlist=["Q"]).Q(type=FinancialRecord.RecordType.EXPENSE),
                default=0,
            ),
        )
        result["net_balance"] = result["total_income"] - result["total_expenses"]
        return result

    # ------------------------------------------------------------------
    # Category distribution
    # ------------------------------------------------------------------
    @staticmethod
    def get_category_distribution() -> list:
        """Returns total amount per category, ordered by total descending."""
        return list(
            FinancialRecord.objects.values("category")
            .annotate(total=Sum("amount"))
            .order_by("-total")
        )

    # ------------------------------------------------------------------
    # Recent activity
    # ------------------------------------------------------------------
    @staticmethod
    def get_recent_activity(limit: int = 5) -> list:
        """Returns the most recent `limit` transactions ordered by date desc."""
        from transactions.serializers import FinancialRecordSerializer

        qs = (
            FinancialRecord.objects.select_related("created_by")
            .order_by("-date", "-id")[:limit]
        )
        return FinancialRecordSerializer(qs, many=True).data

    # ------------------------------------------------------------------
    # Trends (monthly & weekly for the last 6 months)
    # ------------------------------------------------------------------
    @staticmethod
    def get_trends() -> dict:
        """
        Returns monthly and weekly income/expense totals for the last 6 months.
        Uses TruncMonth / TruncWeek so the database handles all grouping.
        """
        six_months_ago = date.today() - relativedelta(months=6)
        base_qs = FinancialRecord.objects.filter(date__gte=six_months_ago)

        from django.db.models import Q

        monthly = list(
            base_qs.annotate(period=TruncMonth("date"))
            .values("period", "type")
            .annotate(total=Sum("amount"))
            .order_by("period", "type")
        )

        weekly = list(
            base_qs.annotate(period=TruncWeek("date"))
            .values("period", "type")
            .annotate(total=Sum("amount"))
            .order_by("period", "type")
        )

        return {"monthly": monthly, "weekly": weekly}
