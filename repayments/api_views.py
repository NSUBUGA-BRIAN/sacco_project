from rest_framework import viewsets
from .models import Repayment
from .serializers import RepaymentSerializer

class RepaymentViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = RepaymentSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_admin:
            return Repayment.objects.all().select_related('loan', 'loan__applicant')
        return Repayment.objects.filter(loan__applicant=user).select_related('loan')
