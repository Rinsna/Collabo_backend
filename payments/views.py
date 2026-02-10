import stripe
from django.conf import settings
from django.db import models
from django.db.models import Q, Sum
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.shortcuts import get_object_or_404
from .models import Payment, Payout
from .serializers import PaymentSerializer, PayoutSerializer
from collaborations.models import Collaboration

stripe.api_key = settings.STRIPE_SECRET_KEY

class PaymentListView(generics.ListAPIView):
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        return Payment.objects.filter(
            Q(payer=user) | Q(payee=user)
        )

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def create_payment_intent(request):
    try:
        collaboration_id = request.data.get('collaboration_id')
        collaboration = get_object_or_404(Collaboration, id=collaboration_id)
        
        # Check if payment already exists
        if hasattr(collaboration, 'payment'):
            return Response(
                {'error': 'Payment already exists for this collaboration'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        amount = int(collaboration.final_rate * 100)  # Convert to cents
        
        # Create Stripe PaymentIntent
        intent = stripe.PaymentIntent.create(
            amount=amount,
            currency='usd',
            metadata={
                'collaboration_id': collaboration.id,
                'payer_id': collaboration.request.company.id,
                'payee_id': collaboration.request.influencer.id,
            }
        )
        
        # Create Payment record
        payment = Payment.objects.create(
            collaboration=collaboration,
            payer=collaboration.request.company,
            payee=collaboration.request.influencer,
            amount=collaboration.final_rate,
            stripe_payment_intent_id=intent.id
        )
        
        return Response({
            'client_secret': intent.client_secret,
            'payment_id': payment.id
        })
        
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def confirm_payment(request):
    try:
        payment_intent_id = request.data.get('payment_intent_id')
        
        # Retrieve PaymentIntent from Stripe
        intent = stripe.PaymentIntent.retrieve(payment_intent_id)
        
        if intent.status == 'succeeded':
            payment = get_object_or_404(
                Payment, 
                stripe_payment_intent_id=payment_intent_id
            )
            payment.status = 'completed'
            payment.save()
            
            # Update collaboration status
            payment.collaboration.status = 'completed'
            payment.collaboration.save()
            
            return Response({'message': 'Payment confirmed successfully'})
        else:
            return Response(
                {'error': 'Payment not successful'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )

class PayoutListCreateView(generics.ListCreateAPIView):
    serializer_class = PayoutSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Payout.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def earnings_summary(request):
    user = request.user
    
    if user.user_type == 'influencer':
        total_earnings = Payment.objects.filter(
            payee=user, 
            status='completed'
        ).aggregate(
            total=Sum('net_amount')
        )['total'] or 0
        
        pending_earnings = Payment.objects.filter(
            payee=user, 
            status__in=['pending', 'processing']
        ).aggregate(
            total=Sum('net_amount')
        )['total'] or 0
        
    elif user.user_type == 'company':
        total_spent = Payment.objects.filter(
            payer=user, 
            status='completed'
        ).aggregate(
            total=Sum('amount')
        )['total'] or 0
        
        pending_payments = Payment.objects.filter(
            payer=user, 
            status__in=['pending', 'processing']
        ).aggregate(
            total=Sum('amount')
        )['total'] or 0
        
        return Response({
            'total_spent': total_spent,
            'pending_payments': pending_payments
        })
    
    return Response({
        'total_earnings': total_earnings,
        'pending_earnings': pending_earnings
    })