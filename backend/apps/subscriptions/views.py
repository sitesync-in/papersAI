from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema
from .models import Plan, CreditWallet, Subscription
from .serializers import PlanSerializer, CreditWalletSerializer, SubscriptionSerializer


class PlanListView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(summary='List all available subscription plans', tags=['Subscriptions'])
    def get(self, request):
        plans = Plan.objects.filter(is_active=True)
        return Response(PlanSerializer(plans, many=True).data)


class WalletView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(summary='Get current user credit wallet balance', tags=['Subscriptions'])
    def get(self, request):
        wallet, _ = CreditWallet.objects.get_or_create(user=request.user, defaults={'credits': 0})
        return Response(CreditWalletSerializer(wallet).data)


class MySubscriptionView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(summary='Get current user subscription', tags=['Subscriptions'])
    def get(self, request):
        try:
            sub = Subscription.objects.get(user=request.user)
            return Response(SubscriptionSerializer(sub).data)
        except Subscription.DoesNotExist:
            return Response({'plan': None, 'is_active': False})
