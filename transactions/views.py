from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from users.models import Profile
from .filters import FinancialRecordFilter
from .models import FinancialRecord
from .permissions import IsAdminForWrite
from .serializers import FinancialRecordSerializer


class FinancialRecordViewSet(viewsets.ModelViewSet):
    """
    CRUD for FinancialRecord with Soft Delete support.

    Permissions:
      - GET          → ADMIN, ANALYST
      - POST/PUT/PATCH/DELETE → ADMIN only
      - POST .../restore/ → ADMIN only

    Filtering:
      - ?date_after=YYYY-MM-DD  (range start, inclusive)
      - ?date_before=YYYY-MM-DD (range end, inclusive)
      - ?category=<value>        (exact)
      - ?type=INCOME|EXPENSE     (exact)
      - ?search=<text>           (searches description)
      - ?include_deleted=true    (ADMIN only)
    """

    serializer_class = FinancialRecordSerializer
    permission_classes = [IsAdminForWrite]

    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = FinancialRecordFilter
    search_fields = ["description"]

    def get_queryset(self):
        """
        Custom queryset logic:
        - Default: Only active records.
        - Admin only: Can pass ?include_deleted=true to see everything.
        """
        user = self.request.user
        
        # Guard for drf-spectacular schema generation
        if getattr(self, "swagger_fake_view", False):
            return FinancialRecord.objects.all_with_deleted().none()

        include_deleted = self.request.query_params.get("include_deleted", "").lower() == "true"

        # Check if user is ADMIN to allow include_deleted
        can_see_deleted = False
        try:
            if user.is_authenticated and user.profile.role == Profile.Role.ADMIN:
                can_see_deleted = True
        except Profile.DoesNotExist:
            pass

        if include_deleted and can_see_deleted:
            return FinancialRecord.objects.all_with_deleted().select_related("created_by")
        
        return FinancialRecord.objects.active().select_related("created_by")

    def perform_create(self, serializer):
        """Automatically assign the authenticated user as created_by."""
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=["post"], url_path="restore")
    def restore(self, request, pk=None):
        """
        POST /api/transactions/records/{id}/restore/
        Exclusively for ADMINs to bring back a soft-deleted record.
        """
        # We must use all_with_deleted() here to find the record even if it's currently hidden
        try:
            instance = FinancialRecord.objects.all_with_deleted().get(pk=pk)
        except FinancialRecord.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        if not instance.is_deleted:
            return Response({"detail": "Record is already active."}, status=status.HTTP_400_BAD_REQUEST)

        instance.restore()
        return Response(self.get_serializer(instance).data, status=status.HTTP_200_OK)
