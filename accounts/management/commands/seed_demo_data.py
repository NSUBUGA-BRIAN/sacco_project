"""
Management command to seed demo data for the SACCO LMS
Run: python manage.py seed_demo_data
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from decimal import Decimal
from django.utils import timezone
from datetime import timedelta

User = get_user_model()


class Command(BaseCommand):
    help = 'Seeds the database with demo data for testing'

    def handle(self, *args, **options):
        self.stdout.write('Seeding demo data...')

        # Create admin user
        admin, created = User.objects.get_or_create(username='admin')
        admin.set_password('admin123')
        admin.first_name = 'System'
        admin.last_name = 'Administrator'
        admin.email = 'admin@sacco.ug'
        admin.role = User.ROLE_ADMIN
        admin.is_staff = True
        admin.is_superuser = True
        admin.phone_number = '+256 700 000 000'
        admin.occupation = 'System Administrator'
        admin.monthly_income = Decimal('5000000')
        admin.save()
        self.stdout.write(self.style.SUCCESS(f'  Admin user: admin / admin123'))

        # Create member users
        members_data = [
            {'username': 'member1', 'first_name': 'Amara', 'last_name': 'Nakamura',
             'email': 'amara@example.com', 'national_id': 'CM001234567',
             'phone': '+256 701 111 111', 'occupation': 'Software Engineer',
             'income': Decimal('3500000'), 'address': 'Kampala, Uganda'},
            {'username': 'member2', 'first_name': 'David', 'last_name': 'Ochieng',
             'email': 'david@example.com', 'national_id': 'CM002345678',
             'phone': '+256 702 222 222', 'occupation': 'Teacher',
             'income': Decimal('1800000'), 'address': 'Entebbe, Uganda'},
            {'username': 'member3', 'first_name': 'Grace', 'last_name': 'Muwanga',
             'email': 'grace@example.com', 'national_id': 'CM003456789',
             'phone': '+256 703 333 333', 'occupation': 'Nurse',
             'income': Decimal('2200000'), 'address': 'Jinja, Uganda'},
        ]

        for md in members_data:
            member, created = User.objects.get_or_create(username=md['username'])
            member.set_password('member123')
            member.first_name = md['first_name']
            member.last_name = md['last_name']
            member.email = md['email']
            member.national_id = md['national_id']
            member.phone_number = md['phone']
            member.occupation = md['occupation']
            member.monthly_income = md['income']
            member.address = md['address']
            member.role = User.ROLE_MEMBER
            member.save()
            self.stdout.write(f'  Member: {md["username"]} / member123')

        # Create loan types
        from loans.models import LoanType, Loan
        loan_types_data = [
            {'name': 'Emergency Loan', 'interest_rate': Decimal('10.00'),
             'min_amount': Decimal('100000'), 'max_amount': Decimal('2000000'),
             'min_duration_months': 1, 'max_duration_months': 12,
             'description': 'Short-term emergency financial assistance'},
            {'name': 'Business Loan', 'interest_rate': Decimal('14.00'),
             'min_amount': Decimal('500000'), 'max_amount': Decimal('20000000'),
             'min_duration_months': 6, 'max_duration_months': 60,
             'description': 'For business development and working capital'},
            {'name': 'School Fees Loan', 'interest_rate': Decimal('8.00'),
             'min_amount': Decimal('200000'), 'max_amount': Decimal('5000000'),
             'min_duration_months': 1, 'max_duration_months': 12,
             'description': 'To cover tuition and education-related costs'},
            {'name': 'Development Loan', 'interest_rate': Decimal('12.00'),
             'min_amount': Decimal('1000000'), 'max_amount': Decimal('50000000'),
             'min_duration_months': 12, 'max_duration_months': 60,
             'description': 'Long-term development projects and investments'},
        ]

        created_loan_types = []
        for ltd in loan_types_data:
            lt, created = LoanType.objects.get_or_create(name=ltd['name'], defaults=ltd)
            if created:
                self.stdout.write(f'  Loan type: {lt.name}')
            created_loan_types.append(lt)

        # Create sample loans
        member1 = User.objects.get(username='member1')
        member2 = User.objects.get(username='member2')
        member3 = User.objects.get(username='member3')

        loans_to_create = [
            {
                'applicant': member1,
                'loan_type': created_loan_types[1],  # Business
                'amount_requested': Decimal('5000000'),
                'repayment_period': 24,
                'purpose': 'Expand my electronics retail shop in Kampala.',
                'status': Loan.STATUS_DISBURSED,
            },
            {
                'applicant': member1,
                'loan_type': created_loan_types[0],  # Emergency
                'amount_requested': Decimal('800000'),
                'repayment_period': 6,
                'purpose': 'Medical emergency for family member.',
                'status': Loan.STATUS_UNDER_REVIEW,
            },
            {
                'applicant': member2,
                'loan_type': created_loan_types[2],  # School fees
                'amount_requested': Decimal('1500000'),
                'repayment_period': 10,
                'purpose': "Children's school fees for this academic year.",
                'status': Loan.STATUS_APPROVED,
            },
            {
                'applicant': member3,
                'loan_type': created_loan_types[3],  # Development
                'amount_requested': Decimal('10000000'),
                'repayment_period': 36,
                'purpose': 'Construction of a rental property.',
                'status': Loan.STATUS_SUBMITTED,
            },
        ]

        for loan_data in loans_to_create:
            if Loan.objects.filter(
                applicant=loan_data['applicant'],
                amount_requested=loan_data['amount_requested'],
                loan_type=loan_data['loan_type']
            ).exists():
                continue

            loan = Loan(**loan_data)
            loan.interest_rate = loan_data['loan_type'].interest_rate
            loan.monthly_installment = loan.calculate_monthly_installment()
            loan.total_repayable = loan.monthly_installment * loan.repayment_period
            loan.reviewed_by = admin
            loan.reviewed_at = timezone.now()
            if loan_data['status'] == Loan.STATUS_DISBURSED:
                loan.disbursed_at = timezone.now() - timedelta(days=60)
            loan.save()
            self.stdout.write(f'  Loan: {loan.loan_id} ({loan.status})')

            # Generate repayment schedule for disbursed loans
            if loan.status == Loan.STATUS_DISBURSED:
                from repayments.services import generate_repayment_schedule
                generate_repayment_schedule(loan)
                self.stdout.write(f'    -> Repayment schedule generated')

            # Add audit log
            from loans.models import LoanAuditLog
            LoanAuditLog.objects.create(
                loan=loan, action='Loan Created', to_status=loan.status,
                performed_by=loan.applicant
            )

        self.stdout.write(self.style.SUCCESS('\n✅ Demo data seeded successfully!'))
        self.stdout.write(self.style.SUCCESS('Login credentials:'))
        self.stdout.write('  Admin:   admin / admin123')
        self.stdout.write('  Member1: member1 / member123')
        self.stdout.write('  Member2: member2 / member123')
        self.stdout.write('  Member3: member3 / member123')
