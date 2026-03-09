from django.contrib import admin
from .models import Plan, Subscription, CreditWallet

@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ['name', 'plan_type', 'price_per_paper', 'monthly_price', 'credits_included', 'is_active']

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ['user', 'plan', 'started_at', 'expires_at', 'is_active']

@admin.register(CreditWallet)
class CreditWalletAdmin(admin.ModelAdmin):
    list_display = ['user', 'credits', 'updated_at']
