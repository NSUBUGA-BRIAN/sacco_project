"""
Dashboard Views - Main landing pages for member and admin
"""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import date, timedelta
from loans.models import Loan
from repayments.models import Repayment
from repayments.services import update_overdue_repayments
from accounts.models import User
from notifications.models import Notification


@login_required
def dashboard_index(request):
    update_overdue_repayments()
    if request.user.is_admin:
        return admin_dashboard(request)
    return member_dashboard(request)


def member_dashboard(request):
    user = request.user
    loans = Loan.objects.filter(applicant=user)

    active_loans = loans.filter(status=Loan.STATUS_DISBURSED)
    pending_loans = loans.filter(status__in=[
        Loan.STATUS_SUBMITTED, Loan.STATUS_UNDER_REVIEW, Loan.STATUS_APPROVED])
    completed_loans = loans.filter(status=Loan.STATUS_COMPLETED)

    # Upcoming repayments
    upcoming_repayments = Repayment.objects.filter(
        loan__applicant=user,
        status=Repayment.STATUS_PENDING,
        due_date__gte=date.today(),
        due_date__lte=date.today() + timedelta(days=30)
    ).select_related('loan').order_by('due_date')[:5]

    overdue_repayments = Repayment.objects.filter(
        loan__applicant=user,
        status=Repayment.STATUS_OVERDUE
    ).select_related('loan')

    # Total amounts
    total_borrowed = active_loans.aggregate(t=Sum('amount_requested'))['t'] or 0
    total_remaining = sum(l.remaining_balance for l in active_loans)

    context = {
        'loans': loans[:5],
        'active_loans_count': active_loans.count(),
        'pending_loans_count': pending_loans.count(),
        'completed_loans_count': completed_loans.count(),
        'upcoming_repayments': upcoming_repayments,
        'overdue_repayments': overdue_repayments,
        'overdue_count': overdue_repayments.count(),
        'total_borrowed': total_borrowed,
        'total_remaining': total_remaining,
    }
    return render(request, 'dashboard/member_dashboard.html', context)


def admin_dashboard(request):
    # Key metrics
    total_members = User.objects.filter(role=User.ROLE_MEMBER).count()
    total_loans = Loan.objects.count()
    loans_by_status = {s: Loan.objects.filter(status=s).count() for s, _ in Loan.STATUS_CHOICES}

    # Financial stats
    total_disbursed = Loan.objects.filter(
        status__in=[Loan.STATUS_DISBURSED, Loan.STATUS_COMPLETED]
    ).aggregate(t=Sum('amount_requested'))['t'] or 0

    total_collected = Repayment.objects.filter(
        status=Repayment.STATUS_PAID
    ).aggregate(t=Sum('amount_paid'))['t'] or 0

    overdue_repayments = Repayment.objects.filter(status=Repayment.STATUS_OVERDUE)
    pending_approvals = Loan.objects.filter(
        status__in=[Loan.STATUS_SUBMITTED, Loan.STATUS_UNDER_REVIEW]
    ).select_related('applicant', 'loan_type')[:10]

    recent_loans = Loan.objects.select_related('applicant').order_by('-application_date')[:8]

    # Chart data: loans by month (last 6 months)
    loan_chart_data = []
    for i in range(5, -1, -1):
        month_date = date.today().replace(day=1) - timedelta(days=i * 30)
        count = Loan.objects.filter(
            application_date__year=month_date.year,
            application_date__month=month_date.month
        ).count()
        loan_chart_data.append({
            'month': month_date.strftime('%b %Y'),
            'count': count
        })

    context = {
        'total_members': total_members,
        'total_loans': total_loans,
        'loans_by_status': loans_by_status,
        'total_disbursed': total_disbursed,
        'total_collected': total_collected,
        'overdue_count': overdue_repayments.count(),
        'pending_approvals': pending_approvals,
        'recent_loans': recent_loans,
        'loan_chart_data': loan_chart_data,
        'pending_count': loans_by_status.get('submitted', 0) + loans_by_status.get('under_review', 0),
    }
    return render(request, 'dashboard/admin_dashboard.html', context)
