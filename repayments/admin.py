from django.contrib import admin
from .models import Repayment

@admin.register(Repayment)
class RepaymentAdmin(admin.ModelAdmin):
    list_display = ('loan', 'installment_number', 'amount_due', 'due_date', 'status', 'paid_date')
    list_filter = ('status',)
    search_fields = ('loan__loan_id',)
