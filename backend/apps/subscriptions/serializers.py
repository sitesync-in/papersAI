from rest_framework import serializers
from .models import Plan, CreditWallet, Subscription


class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = '__all__'


class CreditWalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = CreditWallet
        fields = ['credits', 'updated_at']


class SubscriptionSerializer(serializers.ModelSerializer):
    plan = PlanSerializer(read_only=True)

    class Meta:
        model = Subscription
        fields = ['id', 'plan', 'started_at', 'expires_at', 'is_active']
