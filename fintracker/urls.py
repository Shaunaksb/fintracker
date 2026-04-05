from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    
    # OpenAPI Schema (YAML/JSON)
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    
    # Documentation UIs
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),

    # App APIs
    path("api/users/", include("users.urls", namespace="users")),
    path("api/transactions/", include("transactions.urls", namespace="transactions")),
    path("api/dashboard/", include("dashboard.urls", namespace="dashboard")),
]
