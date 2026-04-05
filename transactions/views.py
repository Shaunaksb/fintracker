from rest_framework import viewsets
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend

from .filters import FinancialRecordFilter
from .models import FinancialRecord
from .permissions import IsAdminForWrite
from .serializers import FinancialRecordSerializer


class FinancialRecordViewSet(viewsets.ModelViewSet):
    """
    CRUD for FinancialRecord.

    Permissions:
      - GET          → ADMIN, ANALYST
      - POST/PUT/PATCH/DELETE → ADMIN only

    Filtering:
      - ?date_after=YYYY-MM-DD  (range start, inclusive)
      - ?date_before=YYYY-MM-DD (range end, inclusive)
      - ?category=<value>        (exact)
      - ?type=INCOME|EXPENSE     (exact)
      - ?search=<text>           (searches description)
    """

    queryset = FinancialRecord.objects.select_related("created_by").all()
    serializer_class = FinancialRecordSerializer
    permission_classes = [IsAdminForWrite]

    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = FinancialRecordFilter
    search_fields = ["description"]

    def perform_create(self, serializer):
        """Automatically assign the authenticated user as created_by."""
        serializer.save(created_by=self.request.user)
