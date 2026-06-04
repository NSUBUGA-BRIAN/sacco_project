"""
Loans Models - Core loan management with workflow states
"""
from django.db import models
from django.conf import settings
from django.utils import timezone
from decimal import Decimal


class LoanType(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2, default=12.00,
        help_text="Annual interest rate (%)")
    min_amount = models.DecimalField(max_digits=12, decimal_places=2, default=100000)
    max_amount = models.DecimalField(max_digits=12, decimal_places=2, default=10000000)
    min_duration_months = models.PositiveIntegerField(default=1)
    max_duration_months = models.PositiveIntegerField(default=60)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.interest_rate}% p.a.)"


class Loan(models.Model):
    # Workflow statuses
    STATUS_DRAFT = 'draft'
    STATUS_SUBMITTED = 'submitted'
    STATUS_UNDER_REVIEW = 'under_review'
    STATUS_APPROVED = 'approved'
    STATUS_REJECTED = 'rejected'
    STATUS_DISBURSED = 'disbursed'
    STATUS_COMPLETED = 'completed'

    STATUS_CHOICES = [
        (STATUS_DRAFT, 'Draft'),
        (STATUS_SUBMITTED, 'Submitted'),
        (STATUS_UNDER_REVIEW, 'Under Review'),
        (STATUS_APPROVED, 'Approved'),
        (STATUS_REJECTED, 'Rejected'),
        (STATUS_DISBURSED, 'Disbursed'),
        (STATUS_COMPLETED, 'Completed'),
    ]

    # Valid workflow transitions
    VALID_TRANSITIONS = {
        STATUS_DRAFT: [STATUS_SUBMITTED],
        STATUS_SUBMITTED: [STATUS_UNDER_REVIEW],
        STATUS_UNDER_REVIEW: [STATUS_APPROVED, STATUS_REJECTED],
        STATUS_APPROVED: [STATUS_DISBURSED],
        STATUS_REJECTED: [],
        STATUS_DISBURSED: [STATUS_COMPLETED],
        STATUS_COMPLETED: [],
    }

    loan_id = models.CharField(max_length=20, unique=True, blank=True)
    applicant = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='loans')
    loan_type = models.ForeignKey(LoanType, on_delete=models.PROTECT, null=True, blank=True)
    amount_requested = models.DecimalField(max_digits=12, decimal_places=2)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2, default=12.00)
    repayment_period = models.PositiveIntegerField(help_text="Duration in months")
    monthly_installment = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_repayable = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    purpose = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_DRAFT)
    application_date = models.DateTimeField(default=timezone.now)
    reviewed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='reviewed_loans')
    reviewed_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True)
    disbursed_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-application_date']

    def __str__(self):
        return f"{self.loan_id} - {self.applicant.get_full_name()} (UGX {self.amount_requested:,})"

    def save(self, *args, **kwargs):
        if not self.loan_id:
            super().save(*args, **kwargs)
            self.loan_id = f"LN-{self.pk:06d}"
            Loan.objects.filter(pk=self.pk).update(loan_id=self.loan_id)
        else:
            super().save(*args, **kwargs)

    def calculate_monthly_installment(self):
        """Calculate monthly installment using reducing balance method."""
        P = Decimal(str(self.amount_requested))
        r = Decimal(str(self.interest_rate)) / Decimal('100') / Decimal('12')  # monthly rate
        n = Decimal(str(self.repayment_period))
        if r == 0:
            return P / n
        installment = P * (r * (1 + r) ** n) / ((1 + r) ** n - 1)
        return round(installment, 2)

    def can_transition_to(self, new_status):
        return new_status in self.VALID_TRANSITIONS.get(self.status, [])

    @property
    def status_badge_class(self):
        badges = {
            self.STATUS_DRAFT: 'secondary',
            self.STATUS_SUBMITTED: 'info',
            self.STATUS_UNDER_REVIEW: 'warning',
            self.STATUS_APPROVED: 'success',
            self.STATUS_REJECTED: 'danger',
            self.STATUS_DISBURSED: 'primary',
            self.STATUS_COMPLETED: 'dark',
        }
        return badges.get(self.status, 'secondary')

    @property
    def amount_paid(self):
        from repayments.models import Repayment
        paid = self.repayments.filter(status=Repayment.STATUS_PAID).aggregate(
            total=models.Sum('amount_paid'))['total'] or Decimal('0')
        return paid

    @property
    def remaining_balance(self):
        return self.total_repayable - self.amount_paid


class LoanAuditLog(models.Model):
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE, related_name='audit_logs')
    action = models.CharField(max_length=100)
    from_status = models.CharField(max_length=20, blank=True)
    to_status = models.CharField(max_length=20, blank=True)
    performed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.loan.loan_id} - {self.action} at {self.timestamp}"
