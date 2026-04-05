from django.contrib import admin

from .models import FinancialRecord


@admin.register(FinancialRecord)
class FinancialRecordAdmin(admin.ModelAdmin):
    list_display = ("id", "type", "category", "amount", "date", "created_by")
    list_filter = ("type", "category", "date")
    search_fields = ("description", "category")
    date_hierarchy = "date"
    ordering = ("-date",)
