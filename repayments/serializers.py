from rest_framework import serializers
from .models import Repayment

class RepaymentSerializer(serializers.ModelSerializer):
    loan_id = serializers.CharField(source='loan.loan_id', read_only=True)
    class Meta:
        model = Repayment
        fields = '__all__'
