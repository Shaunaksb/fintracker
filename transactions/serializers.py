from rest_framework import serializers

from .models import FinancialRecord


class FinancialRecordSerializer(serializers.ModelSerializer):
    created_by = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = FinancialRecord
        fields = (
            "id",
            "amount",
            "type",
            "category",
            "date",
            "description",
            "created_by",
        )
        read_only_fields = ("id", "created_by")

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than zero.")
        return value
