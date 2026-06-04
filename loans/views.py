"""
Loans Views
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import Loan, LoanType, LoanAuditLog
from .forms import LoanApplicationForm, LoanReviewForm
from .services import (validate_loan_application, submit_loan, review_loan,
                        approve_loan, reject_loan, disburse_loan, LoanValidationError)


@login_required
def loan_list_view(request):
    """Member: see their own loans. Admin: see all loans."""
    if request.user.is_admin:
        loans = Loan.objects.select_related('applicant', 'loan_type').all()
        # Filter by status if requested
        status_filter = request.GET.get('status', '')
        if status_filter:
            loans = loans.filter(status=status_filter)
    else:
        loans = Loan.objects.filter(applicant=request.user).select_related('loan_type')

    context = {
        'loans': loans,
        'status_choices': Loan.STATUS_CHOICES,
        'status_filter': request.GET.get('status', ''),
    }
    return render(request, 'loans/loan_list.html', context)


@login_required
def loan_apply_view(request):
    """Member applies for a new loan."""
    if request.user.is_admin:
        messages.error(request, 'Administrators cannot apply for loans.')
        return redirect('loans:list')

    if request.method == 'POST':
        form = LoanApplicationForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount_requested']
            duration = form.cleaned_data['repayment_period']
            errors = validate_loan_application(request.user, amount, duration)
            if errors:
                for e in errors:
                    messages.error(request, e)
            else:
                loan = form.save(commit=False)
                loan.applicant = request.user
                loan.interest_rate = loan.loan_type.interest_rate if loan.loan_type else 12
                loan.monthly_installment = loan.calculate_monthly_installment()
                loan.total_repayable = loan.monthly_installment * loan.repayment_period
                loan.save()
                messages.success(request, f'Loan application {loan.loan_id} saved as draft.')
                return redirect('loans:detail', pk=loan.pk)
    else:
        form = LoanApplicationForm()

    loan_types = LoanType.objects.filter(is_active=True)
    return render(request, 'loans/loan_apply.html', {'form': form, 'loan_types': loan_types})


@login_required
def loan_detail_view(request, pk):
    loan = get_object_or_404(Loan, pk=pk)
    if not request.user.is_admin and loan.applicant != request.user:
        messages.error(request, 'Access denied.')
        return redirect('loans:list')

    audit_logs = loan.audit_logs.select_related('performed_by').all()
    repayments = loan.repayments.all() if hasattr(loan, 'repayments') else []

    context = {
        'loan': loan,
        'audit_logs': audit_logs,
        'repayments': repayments,
        'review_form': LoanReviewForm() if request.user.is_admin else None,
    }
    return render(request, 'loans/loan_detail.html', context)


@login_required
def loan_submit_view(request, pk):
    """Member submits draft loan."""
    loan = get_object_or_404(Loan, pk=pk, applicant=request.user)
    if request.method == 'POST':
        try:
            submit_loan(loan, request.user)
            messages.success(request, f'Loan {loan.loan_id} submitted for review.')
        except LoanValidationError as e:
            messages.error(request, str(e))
    return redirect('loans:detail', pk=pk)


@login_required
def loan_action_view(request, pk):
    """Admin actions: review, approve, reject, disburse."""
    if not request.user.is_admin:
        messages.error(request, 'Access denied.')
        return redirect('loans:list')

    loan = get_object_or_404(Loan, pk=pk)

    if request.method == 'POST':
        action = request.POST.get('action')
        try:
            if action == 'review':
                review_loan(loan, request.user)
                messages.success(request, f'Loan {loan.loan_id} moved to Under Review.')
            elif action == 'approve':
                notes = request.POST.get('notes', '')
                approve_loan(loan, request.user, notes)
                messages.success(request, f'Loan {loan.loan_id} approved successfully.')
            elif action == 'reject':
                reason = request.POST.get('rejection_reason', '')
                if not reason:
                    messages.error(request, 'Please provide a rejection reason.')
                    return redirect('loans:detail', pk=pk)
                reject_loan(loan, request.user, reason)
                messages.success(request, f'Loan {loan.loan_id} rejected.')
            elif action == 'disburse':
                disburse_loan(loan, request.user)
                messages.success(request, f'Loan {loan.loan_id} disbursed. Repayment schedule generated.')
        except LoanValidationError as e:
            messages.error(request, str(e))

    return redirect('loans:detail', pk=pk)


@login_required
def calculate_installment_api(request):
    """AJAX endpoint to calculate monthly installment."""
    try:
        amount = float(request.GET.get('amount', 0))
        duration = int(request.GET.get('duration', 0))
        rate = float(request.GET.get('rate', 12))

        if amount <= 0 or duration <= 0:
            return JsonResponse({'error': 'Invalid values'}, status=400)

        from decimal import Decimal
        from loans.models import Loan as L
        dummy = type('obj', (object,), {
            'amount_requested': Decimal(str(amount)),
            'interest_rate': Decimal(str(rate)),
            'repayment_period': duration,
        })()

        loan_obj = Loan()
        loan_obj.amount_requested = Decimal(str(amount))
        loan_obj.interest_rate = Decimal(str(rate))
        loan_obj.repayment_period = duration
        installment = loan_obj.calculate_monthly_installment()
        total = installment * duration

        return JsonResponse({
            'monthly_installment': float(installment),
            'total_repayable': float(total),
            'total_interest': float(total - Decimal(str(amount))),
        })
    except (ValueError, TypeError) as e:
        return JsonResponse({'error': str(e)}, status=400)
