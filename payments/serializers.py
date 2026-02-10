from rest_framework import serializers
from .models import Payment, Payout

class PaymentSerializer(serializers.ModelSerializer):
    collaboration_title = serializers.CharField(source='collaboration.request.campaign.title', read_only=True)
    payer_username = serializers.CharField(source='payer.username', read_only=True)
    payee_username = serializers.CharField(source='payee.username', read_only=True)
    
    class Meta:
        model = Payment
        fields = '__all__'
        read_only_fields = ('platform_fee', 'net_amount', 'stripe_payment_intent_id')

class PayoutSerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = Payout
        fields = '__all__'
        read_only_fields = ('user', 'stripe_transfer_id')