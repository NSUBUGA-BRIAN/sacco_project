"""
Repayments Services - Schedule generation and payment processing
"""
from django.utils import timezone
from datetime import date, timedelta
from decimal import Decimal
from dateutil.relativedelta import relativedelta
import calendar


def generate_repayment_schedule(loan):
    """Generate repayment schedule for a disbursed loan."""
    from .models import Repayment

    # Delete existing schedule if any
    Repayment.objects.filter(loan=loan).delete()

    monthly_installment = loan.monthly_installment
    disbursement_date = loan.disbursed_at.date() if loan.disbursed_at else date.today()

    repayments = []
    running_balance = loan.total_repayable

    for i in range(1, loan.repayment_period + 1):
        # Due date = disbursement day + i months
        due_date = disbursement_date + relativedelta(months=i)
        running_balance -= monthly_installment

        repayments.append(Repayment(
            loan=loan,
            installment_number=i,
            amount_due=monthly_installment,
            due_date=due_date,
            status=Repayment.STATUS_PENDING,
            remaining_balance=max(running_balance, Decimal('0'))
        ))

    Repayment.objects.bulk_create(repayments)
    return repayments


def record_payment(repayment, amount_paid, user=None):
    """Record a payment against a repayment installment."""
    from notifications.services import create_notification

    repayment.amount_paid = Decimal(str(amount_paid))
    repayment.paid_date = date.today()
    repayment.status = Repayment.STATUS_PAID if amount_paid >= repayment.amount_due else Repayment.STATUS_PENDING
    repayment.save()

    # Check if all repayments are complete
    loan = repayment.loan
    all_paid = not loan.repayments.exclude(status='paid').exists()
    if all_paid:
        loan.status = 'completed'
        loan.completed_at = timezone.now()
        loan.save()
        create_notification(loan.applicant,
            f"Congratulations! Your loan {loan.loan_id} is fully repaid.",
            'loan_completed', loan.id)

    # Send payment confirmation notification
    create_notification(loan.applicant,
        f"Payment of UGX {amount_paid:,} recorded for installment #{repayment.installment_number}.",
        'payment_recorded', loan.id)

    return repayment


def update_overdue_repayments():
    """Batch update overdue repayments - run via management command or cron."""
    from .models import Repayment
    today = date.today()
    overdue = Repayment.objects.filter(status=Repayment.STATUS_PENDING, due_date__lt=today)
    count = overdue.update(status=Repayment.STATUS_OVERDUE)
    return count


# Make Repayment importable from services
from .models import Repayment
