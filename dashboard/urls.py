from django.urls import path

from .views import (
    DashboardCategoryView,
    DashboardRecentView,
    DashboardSummaryView,
    DashboardTotalsView,
    DashboardTrendsView,
)

app_name = "dashboard"

urlpatterns = [
    path("summary/", DashboardSummaryView.as_view(), name="summary"),
    path("totals/", DashboardTotalsView.as_view(), name="totals"),
    path("categories/", DashboardCategoryView.as_view(), name="categories"),
    path("recent/", DashboardRecentView.as_view(), name="recent"),
    path("trends/", DashboardTrendsView.as_view(), name="trends"),
]
