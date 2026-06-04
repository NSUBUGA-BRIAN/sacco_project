"""
Loans Services - Business logic and validation layer
"""
from django.conf import settings
from django.utils import timezone
from decimal import Decimal
from .models import Loan, LoanAuditLog
from repayments.services import generate_repayment_schedule
from notifications.services import create_notification


class LoanValidationError(Exception):
    pass


def validate_loan_application(user, amount, duration):
    """Validate loan application against business rules."""
    errors = []

    # Rule 1: Amount must be positive
    if amount <= 0:
        errors.append("Loan amount must be greater than zero.")

    # Rule 2: Duration must be valid
    if duration <= 0 or duration > 60:
        errors.append("Loan duration must be between 1 and 60 months.")

    # Rule 3: Check for overdue loans
    from repayments.models import Repayment
    overdue_loans = Loan.objects.filter(
        applicant=user,
        status=Loan.STATUS_DISBURSED,
        repayments__status=Repayment.STATUS_OVERDUE
    ).distinct()
    if overdue_loans.exists():
        errors.append("You cannot apply for a new loan while you have overdue payments.")

    # Rule 4: Check for active pending loans
    active_statuses = [Loan.STATUS_SUBMITTED, Loan.STATUS_UNDER_REVIEW, Loan.STATUS_APPROVED]
    pending = Loan.objects.filter(applicant=user, status__in=active_statuses)
    if pending.exists():
        errors.append("You already have an active loan application in progress.")

    # Rule 5: Income-based limit
    max_loan = Decimal(str(user.monthly_income)) * Decimal(str(getattr(settings, 'MAX_LOAN_MULTIPLIER', 3)))
    if Decimal(str(amount)) > max_loan and max_loan > 0:
        errors.append(f"Maximum loan amount based on your income is UGX {max_loan:,.0f}.")

    return errors


def submit_loan(loan, user):
    """Submit a draft loan for review."""
    if not loan.can_transition_to(Loan.STATUS_SUBMITTED):
        raise LoanValidationError("This loan cannot be submitted in its current state.")

    old_status = loan.status
    loan.status = Loan.STATUS_SUBMITTED
    loan.save()

    LoanAuditLog.objects.create(
        loan=loan, action='Loan Submitted',
        from_status=old_status, to_status=loan.status,
        performed_by=user, notes='Member submitted loan for review.'
    )
    create_notification(user, f"Your loan {loan.loan_id} has been submitted successfully.",
                        'loan_submitted', loan.id)
    return loan


def review_loan(loan, admin_user):
    """Move loan to Under Review status."""
    if not loan.can_transition_to(Loan.STATUS_UNDER_REVIEW):
        raise LoanValidationError("This loan cannot be moved to review.")

    old_status = loan.status
    loan.status = Loan.STATUS_UNDER_REVIEW
    loan.reviewed_by = admin_user
    loan.reviewed_at = timezone.now()
    loan.save()

    LoanAuditLog.objects.create(
        loan=loan, action='Under Review',
        from_status=old_status, to_status=loan.status,
        performed_by=admin_user
    )
    create_notification(loan.applicant, f"Your loan {loan.loan_id} is now under review.",
                        'loan_review', loan.id)
    return loan


def approve_loan(loan, admin_user, notes=''):
    """Approve a loan application."""
    if not loan.can_transition_to(Loan.STATUS_APPROVED):
        raise LoanValidationError("This loan cannot be approved in its current state.")

    old_status = loan.status
    loan.status = Loan.STATUS_APPROVED
    loan.reviewed_by = admin_user
    loan.reviewed_at = timezone.now()
    loan.notes = notes
    loan.save()

    LoanAuditLog.objects.create(
        loan=loan, action='Loan Approved',
        from_status=old_status, to_status=loan.status,
        performed_by=admin_user, notes=notes
    )
    create_notification(loan.applicant,
        f"Congratulations! Your loan {loan.loan_id} of UGX {loan.amount_requested:,} has been approved.",
        'loan_approved', loan.id)
    return loan


def reject_loan(loan, admin_user, reason):
    """Reject a loan application."""
    if not loan.can_transition_to(Loan.STATUS_REJECTED):
        raise LoanValidationError("This loan cannot be rejected in its current state.")

    old_status = loan.status
    loan.status = Loan.STATUS_REJECTED
    loan.reviewed_by = admin_user
    loan.reviewed_at = timezone.now()
    loan.rejection_reason = reason
    loan.save()

    LoanAuditLog.objects.create(
        loan=loan, action='Loan Rejected',
        from_status=old_status, to_status=loan.status,
        performed_by=admin_user, notes=reason
    )
    create_notification(loan.applicant,
        f"Your loan application {loan.loan_id} has been rejected. Reason: {reason}",
        'loan_rejected', loan.id)
    return loan


def disburse_loan(loan, admin_user):
    """Disburse an approved loan and generate repayment schedule."""
    if not loan.can_transition_to(Loan.STATUS_DISBURSED):
        raise LoanValidationError("This loan cannot be disbursed in its current state.")

    old_status = loan.status
    loan.status = Loan.STATUS_DISBURSED
    loan.disbursed_at = timezone.now()
    loan.save()

    # Generate repayment schedule
    generate_repayment_schedule(loan)

    LoanAuditLog.objects.create(
        loan=loan, action='Loan Disbursed',
        from_status=old_status, to_status=loan.status,
        performed_by=admin_user
    )
    create_notification(loan.applicant,
        f"Your loan {loan.loan_id} has been disbursed. Check your repayment schedule.",
        'loan_disbursed', loan.id)
    return loan
