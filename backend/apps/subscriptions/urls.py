from django.urls import path
from .views import PlanListView, WalletView, MySubscriptionView

urlpatterns = [
    path('plans/', PlanListView.as_view(), name='plan-list'),
    path('wallet/', WalletView.as_view(), name='wallet'),
    path('my/', MySubscriptionView.as_view(), name='my-subscription'),
]
