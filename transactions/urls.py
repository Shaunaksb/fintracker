from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import FinancialRecordViewSet

app_name = "transactions"

router = DefaultRouter()
router.register(r"records", FinancialRecordViewSet, basename="financial-record")

urlpatterns = [
    path("", include(router.urls)),
]
