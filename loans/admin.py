from django.contrib import admin
from .models import Loan, LoanType, LoanAuditLog

@admin.register(LoanType)
class LoanTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'interest_rate', 'min_amount', 'max_amount', 'is_active')

@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display = ('loan_id', 'applicant', 'amount_requested', 'status', 'application_date')
    list_filter = ('status', 'loan_type')
    search_fields = ('loan_id', 'applicant__username', 'applicant__email')

@admin.register(LoanAuditLog)
class LoanAuditLogAdmin(admin.ModelAdmin):
    list_display = ('loan', 'action', 'from_status', 'to_status', 'performed_by', 'timestamp')
    readonly_fields = ('timestamp',)
