from django.urls import path
from .views import (
    PaymentListView, PayoutListCreateView,
    create_payment_intent, confirm_payment, earnings_summary,
    AdminPaymentListView, AdminPayoutListView
)

urlpatterns = [
    path('payments/', PaymentListView.as_view(), name='payments'),
    path('create-payment-intent/', create_payment_intent, name='create-payment-intent'),
    path('confirm-payment/', confirm_payment, name='confirm-payment'),
    path('payouts/', PayoutListCreateView.as_view(), name='payouts'),
    path('earnings/', earnings_summary, name='earnings-summary'),
    
    # Admin endpoints
    path('admin/payments/', AdminPaymentListView.as_view(), name='admin-payments'),
    path('admin/payouts/', AdminPayoutListView.as_view(), name='admin-payouts'),
]