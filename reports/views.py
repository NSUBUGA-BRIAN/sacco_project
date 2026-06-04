"""
Reports Views - Financial and management reports
"""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import date, timedelta
from loans.models import Loan
from repayments.models import Repayment
from accounts.models import User


@login_required
def reports_index(request):
    if not request.user.is_admin:
        from django.contrib import messages
        messages.error(request, 'Access denied. Admin only.')
        return redirect('dashboard:index')

    # Summary stats
    total_members = User.objects.filter(role=User.ROLE_MEMBER).count()
    active_members = User.objects.filter(role=User.ROLE_MEMBER, is_active=True).count()

    loans_summary = {
        status: Loan.objects.filter(status=status).aggregate(
            count=Count('id'), total=Sum('amount_requested')
        ) for status, _ in Loan.STATUS_CHOICES
    }

    total_disbursed = Loan.objects.filter(
        status__in=[Loan.STATUS_DISBURSED, Loan.STATUS_COMPLETED]
    ).aggregate(t=Sum('amount_requested'))['t'] or 0

    total_collected = Repayment.objects.filter(
        status='paid'
    ).aggregate(t=Sum('amount_paid'))['t'] or 0

    overdue_amount = Repayment.objects.filter(
        status='overdue'
    ).aggregate(t=Sum('amount_due'))['t'] or 0

    # Recent 12 months
    monthly_data = []
    for i in range(11, -1, -1):
        d = date.today().replace(day=1) - timedelta(days=i * 30)
        disbursed = Loan.objects.filter(
            disbursed_at__year=d.year, disbursed_at__month=d.month
        ).aggregate(t=Sum('amount_requested'))['t'] or 0
        collected = Repayment.objects.filter(
            paid_date__year=d.year, paid_date__month=d.month, status='paid'
        ).aggregate(t=Sum('amount_paid'))['t'] or 0
        monthly_data.append({
            'month': d.strftime('%b %Y'),
            'disbursed': float(disbursed),
            'collected': float(collected),
        })

    # Top borrowers
    top_borrowers = User.objects.filter(role=User.ROLE_MEMBER).annotate(
        loan_count=Count('loans'),
        total_borrowed=Sum('loans__amount_requested')
    ).filter(loan_count__gt=0).order_by('-total_borrowed')[:10]

    context = {
        'total_members': total_members,
        'active_members': active_members,
        'loans_summary': loans_summary,
        'total_disbursed': total_disbursed,
        'total_collected': total_collected,
        'overdue_amount': overdue_amount,
        'monthly_data': monthly_data,
        'top_borrowers': top_borrowers,
    }
    return render(request, 'reports/reports.html', context)
