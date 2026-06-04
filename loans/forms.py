"""
Loans Forms
"""
from django import forms
from .models import Loan, LoanType


class LoanApplicationForm(forms.ModelForm):
    class Meta:
        model = Loan
        fields = ('loan_type', 'amount_requested', 'repayment_period', 'purpose')
        widgets = {
            'amount_requested': forms.NumberInput(attrs={
                'placeholder': 'Amount in UGX', 'min': '100000', 'step': '50000'}),
            'repayment_period': forms.NumberInput(attrs={
                'placeholder': 'Number of months', 'min': '1', 'max': '60'}),
            'purpose': forms.Textarea(attrs={
                'rows': 4, 'placeholder': 'Describe why you need this loan...'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['loan_type'].queryset = LoanType.objects.filter(is_active=True)
        self.fields['loan_type'].empty_label = "-- Select Loan Type --"


class LoanReviewForm(forms.Form):
    action = forms.ChoiceField(choices=[
        ('approve', 'Approve'),
        ('reject', 'Reject'),
    ])
    notes = forms.CharField(required=False,
        widget=forms.Textarea(attrs={'rows': 3, 'placeholder': 'Additional notes...'}))
    rejection_reason = forms.CharField(required=False,
        widget=forms.Textarea(attrs={'rows': 3, 'placeholder': 'Reason for rejection (required if rejecting)...'}))

    def clean(self):
        cleaned_data = super().clean()
        action = cleaned_data.get('action')
        rejection_reason = cleaned_data.get('rejection_reason')
        if action == 'reject' and not rejection_reason:
            raise forms.ValidationError("Please provide a reason for rejection.")
        return cleaned_data
