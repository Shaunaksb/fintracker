from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .services import FinanceAnalytics


class DashboardSummaryView(APIView):
    """
    GET /api/dashboard/summary/

    Accessible by ALL authenticated roles (ADMIN, ANALYST, VIEWER).
    Returns a single consolidated payload with all analytics.
    Calculation logic lives entirely in FinanceAnalytics (services.py).
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        data = {
            "totals": FinanceAnalytics.get_totals(),
            "category_distribution": FinanceAnalytics.get_category_distribution(),
            "recent_activity": FinanceAnalytics.get_recent_activity(limit=5),
            "trends": FinanceAnalytics.get_trends(),
        }
        return Response(data)


class DashboardTotalsView(APIView):
    """GET /api/dashboard/totals/ — income, expenses, net balance."""

    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        return Response(FinanceAnalytics.get_totals())


class DashboardCategoryView(APIView):
    """GET /api/dashboard/categories/ — total per category."""

    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        return Response(FinanceAnalytics.get_category_distribution())


class DashboardRecentView(APIView):
    """GET /api/dashboard/recent/?limit=5 — most recent transactions."""

    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            limit = int(request.query_params.get("limit", 5))
            # Clamp limit between 1 and 50
            limit = max(1, min(50, limit))
        except (TypeError, ValueError):
            limit = 5
        return Response(FinanceAnalytics.get_recent_activity(limit=limit))


class DashboardTrendsView(APIView):
    """GET /api/dashboard/trends/ — monthly & weekly totals for last 6 months."""

    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        return Response(FinanceAnalytics.get_trends())
