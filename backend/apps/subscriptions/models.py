from django.db import models
from django.conf import settings


class Plan(models.Model):
    PLAN_FREE = 'free'
    PLAN_PAYG = 'payg'
    PLAN_SCHOOL = 'school'
    PLAN_B2G = 'b2g'
    PLAN_CHOICES = [
        (PLAN_FREE, 'Free'),
        (PLAN_PAYG, 'Pay As You Go'),
        (PLAN_SCHOOL, 'School Plan'),
        (PLAN_B2G, 'State-Wide B2G'),
    ]

    name = models.CharField(max_length=100)
    plan_type = models.CharField(max_length=20, choices=PLAN_CHOICES, unique=True)
    price_per_paper = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    monthly_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    credits_included = models.IntegerField(default=0)
    description = models.TextField(blank=True)
    features = models.JSONField(default=list)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Subscription(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='subscription')
    plan = models.ForeignKey(Plan, on_delete=models.SET_NULL, null=True)
    started_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user} — {self.plan}"


class CreditWallet(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='wallet')
    credits = models.IntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.get_full_name()} — {self.credits} credits"
