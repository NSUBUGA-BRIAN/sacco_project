"""
Repayments Views
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Repayment
from .services import record_payment, update_overdue_repayments
from loans.models import Loan


@login_required
def repayment_list_view(request):
    """Show repayments - member sees own, admin sees all."""
    update_overdue_repayments()  # Update overdue statuses

    if request.user.is_admin:
        repayments = Repayment.objects.select_related('loan', 'loan__applicant').all()
        status_filter = request.GET.get('status', '')
        if status_filter:
            repayments = repayments.filter(status=status_filter)
    else:
        repayments = Repayment.objects.filter(
            loan__applicant=request.user
        ).select_related('loan')

    context = {
        'repayments': repayments,
        'status_choices': Repayment.STATUS_CHOICES,
        'status_filter': request.GET.get('status', ''),
    }
    return render(request, 'repayments/repayment_list.html', context)


@login_required
def loan_repayments_view(request, loan_pk):
    """Repayment schedule for a specific loan."""
    loan = get_object_or_404(Loan, pk=loan_pk)
    if not request.user.is_admin and loan.applicant != request.user:
        messages.error(request, 'Access denied.')
        return redirect('repayments:list')

    update_overdue_repayments()
    repayments = loan.repayments.all()

    context = {
        'loan': loan,
        'repayments': repayments,
        'paid_count': repayments.filter(status='paid').count(),
        'pending_count': repayments.filter(status='pending').count(),
        'overdue_count': repayments.filter(status='overdue').count(),
    }
    return render(request, 'repayments/loan_repayments.html', context)


@login_required
def record_payment_view(request, pk):
    """Admin records a payment."""
    if not request.user.is_admin:
        messages.error(request, 'Access denied.')
        return redirect('repayments:list')

    repayment = get_object_or_404(Repayment, pk=pk)

    if request.method == 'POST':
        try:
            amount = float(request.POST.get('amount_paid', 0))
            if amount <= 0:
                messages.error(request, 'Invalid payment amount.')
            else:
                record_payment(repayment, amount, request.user)
                messages.success(request,
                    f'Payment of UGX {amount:,.0f} recorded for {repayment.loan.loan_id}.')
        except (ValueError, TypeError):
            messages.error(request, 'Invalid payment amount.')
        return redirect('repayments:loan_repayments', loan_pk=repayment.loan.pk)

    return render(request, 'repayments/record_payment.html', {'repayment': repayment})
