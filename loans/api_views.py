from rest_framework import viewsets, permissions
from .models import Loan
from .serializers import LoanSerializer


class LoanViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = LoanSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_admin:
            return Loan.objects.all().select_related('applicant', 'loan_type')
        return Loan.objects.filter(applicant=user).select_related('loan_type')
