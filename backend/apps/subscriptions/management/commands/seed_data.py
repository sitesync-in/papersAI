"""
Management command to seed initial data (plans, demo users).
Usage: python manage.py seed_data
"""
from django.core.management.base import BaseCommand
from apps.subscriptions.models import Plan, CreditWallet
from apps.accounts.models import User
from apps.students.models import StudentClass


class Command(BaseCommand):
    help = 'Seed initial data: plans, demo teacher, demo class'

    def handle(self, *args, **options):
        # Create Plans
        plans_data = [
            {
                'name': 'Free Trial',
                'plan_type': 'free',
                'price_per_paper': 0,
                'monthly_price': 0,
                'credits_included': 50,
                'description': '50 free credits to get started',
                'features': ['50 papers', 'PDF download', 'Email support'],
            },
            {
                'name': 'Pay As You Go',
                'plan_type': 'payg',
                'price_per_paper': 15,
                'monthly_price': 0,
                'credits_included': 0,
                'description': '₹15 per paper, no commitment',
                'features': ['Unlimited papers', 'PDF download', 'Priority support', 'Answer keys'],
            },
            {
                'name': 'School Plan',
                'plan_type': 'school',
                'price_per_paper': 10,
                'monthly_price': 2999,
                'credits_included': 500,
                'description': '₹10 per paper, unlimited teacher accounts',
                'features': ['500 papers/month', 'Unlimited teachers', 'Admin dashboard', 'Priority support', 'Bulk download'],
            },
            {
                'name': 'State-Wide B2G Rollout',
                'plan_type': 'b2g',
                'price_per_paper': 5,
                'monthly_price': 0,
                'credits_included': 10000,
                'description': 'Custom deployment on RajMegh State Cloud',
                'features': ['Custom deployment', 'RajMegh integration', 'Dedicated support', 'SLA guarantee', 'Hindi support'],
            },
        ]

        for pd in plans_data:
            plan, created = Plan.objects.get_or_create(
                plan_type=pd['plan_type'],
                defaults=pd
            )
            status = 'Created' if created else 'Already exists'
            self.stdout.write(f"  Plan '{plan.name}': {status}")

        # Create demo teacher
        if not User.objects.filter(username='gajendra').exists():
            teacher = User.objects.create_user(
                username='gajendra',
                email='gajendra@school.rj.gov.in',
                password='password123',
                first_name='Gajendra',
                last_name='Prajapat',
                role='teacher',
                school_name='Govt. Sr. Sec. School',
                district='Jaipur',
            )
            CreditWallet.objects.create(user=teacher, credits=150)
            StudentClass.objects.create(
                teacher=teacher, name='Class 10A', board='RBSE', section='A'
            )
            StudentClass.objects.create(
                teacher=teacher, name='Class 12C', board='RBSE', section='C'
            )
            self.stdout.write(self.style.SUCCESS("  Demo teacher 'gajendra' created (password: password123)"))
        else:
            self.stdout.write("  Demo teacher 'gajendra' already exists")

        self.stdout.write(self.style.SUCCESS('\nSeed data completed!'))
