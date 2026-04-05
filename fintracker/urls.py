from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/users/", include("users.urls", namespace="users")),
    path("api/transactions/", include("transactions.urls", namespace="transactions")),
    path("api/dashboard/", include("dashboard.urls", namespace="dashboard")),
]
