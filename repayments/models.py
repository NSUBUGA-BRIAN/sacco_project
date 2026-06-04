"""
Repayments Models
"""
from django.db import models
from django.utils import timezone
from decimal import Decimal


class Repayment(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_PAID = 'paid'
    STATUS_OVERDUE = 'overdue'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_PAID, 'Paid'),
        (STATUS_OVERDUE, 'Overdue'),
    ]

    loan = models.ForeignKey('loans.Loan', on_delete=models.CASCADE, related_name='repayments')
    installment_number = models.PositiveIntegerField()
    amount_due = models.DecimalField(max_digits=12, decimal_places=2)
    amount_paid = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    due_date = models.DateField()
    paid_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_PENDING)
    remaining_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['installment_number']
        unique_together = ('loan', 'installment_number')

    def __str__(self):
        return f"{self.loan.loan_id} - Installment #{self.installment_number} ({self.status})"

    @property
    def is_overdue(self):
        return self.status == self.STATUS_PENDING and self.due_date < timezone.now().date()

    def check_and_update_overdue(self):
        """Update status to overdue if past due date."""
        if self.status == self.STATUS_PENDING and self.due_date < timezone.now().date():
            self.status = self.STATUS_OVERDUE
            self.save()
            return True
        return False
