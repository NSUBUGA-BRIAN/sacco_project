from rest_framework import serializers
from .models import Loan, LoanType


class LoanTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoanType
        fields = '__all__'


class LoanSerializer(serializers.ModelSerializer):
    applicant_name = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Loan
        fields = ('id', 'loan_id', 'applicant', 'applicant_name', 'loan_type',
                  'amount_requested', 'interest_rate', 'repayment_period',
                  'monthly_installment', 'total_repayable', 'purpose',
                  'status', 'status_display', 'application_date')
        read_only_fields = ('loan_id', 'monthly_installment', 'total_repayable')

    def get_applicant_name(self, obj):
        return obj.applicant.get_full_name()
