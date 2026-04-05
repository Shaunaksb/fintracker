import decimal
from datetime import date

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

    # ── Field-level validation ───────────────────────────────────────────────

    def validate_amount(self, value):
        """Must be positive and have at most 2 decimal places."""
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than zero.")
        # Guard against values like 10.999 sneaking past DecimalField rounding
        if value.as_tuple().exponent < -2:
            raise serializers.ValidationError(
                "Amount must have at most 2 decimal places."
            )
        return value

    def validate_type(self, value):
        valid = [choice[0] for choice in FinancialRecord.RecordType.choices]
        if value not in valid:
            raise serializers.ValidationError(
                f"Invalid type. Must be one of: {', '.join(valid)}."
            )
        return value

    def validate_category(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Category cannot be blank.")
        if len(value) > 100:
            raise serializers.ValidationError(
                "Category must be 100 characters or fewer."
            )
        return value

    def validate_date(self, value):
        if value > date.today():
            raise serializers.ValidationError(
                "Date cannot be in the future."
            )
        return value

    def validate_description(self, value):
        return value.strip() if value else ""

    # ── Object-level validation ──────────────────────────────────────────────

    def validate(self, attrs):
        # Ensure amount is present on partial updates too
        amount = attrs.get("amount")
        if amount is not None and amount <= 0:
            raise serializers.ValidationError({"amount": "Amount must be greater than zero."})
        return attrs
