"""Create default loan types for deployment."""

from decimal import Decimal
from django.core.management.base import BaseCommand
from loans.models import LoanType


class Command(BaseCommand):
    help = 'Creates default loan types if they do not already exist.'

    def handle(self, *args, **options):
        default_loan_types = [
            {
                'name': 'Emergency Loan',
                'interest_rate': Decimal('10.00'),
                'min_amount': Decimal('100000'),
                'max_amount': Decimal('2000000'),
                'min_duration_months': 1,
                'max_duration_months': 12,
                'description': 'Short-term emergency financial assistance',
                'is_active': True,
            },
            {
                'name': 'Business Loan',
                'interest_rate': Decimal('14.00'),
                'min_amount': Decimal('500000'),
                'max_amount': Decimal('20000000'),
                'min_duration_months': 6,
                'max_duration_months': 60,
                'description': 'For business development and working capital',
                'is_active': True,
            },
            {
                'name': 'School Fees Loan',
                'interest_rate': Decimal('8.00'),
                'min_amount': Decimal('200000'),
                'max_amount': Decimal('5000000'),
                'min_duration_months': 1,
                'max_duration_months': 12,
                'description': 'To cover tuition and education-related costs',
                'is_active': True,
            },
            {
                'name': 'Development Loan',
                'interest_rate': Decimal('12.00'),
                'min_amount': Decimal('1000000'),
                'max_amount': Decimal('50000000'),
                'min_duration_months': 12,
                'max_duration_months': 60,
                'description': 'Long-term development projects and investments',
                'is_active': True,
            },
        ]

        for loan_type_data in default_loan_types:
            loan_type, created = LoanType.objects.get_or_create(
                name=loan_type_data['name'],
                defaults=loan_type_data
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created loan type: {loan_type.name}"))
            else:
                updated = False
                for field, value in loan_type_data.items():
                    if getattr(loan_type, field) != value:
                        setattr(loan_type, field, value)
                        updated = True
                if updated:
                    loan_type.save()
                    self.stdout.write(self.style.SUCCESS(f"Updated loan type: {loan_type.name}"))
                else:
                    self.stdout.write(self.style.NOTICE(f"Loan type already exists: {loan_type.name}"))

        self.stdout.write(self.style.SUCCESS('Default loan types initialization complete.'))
