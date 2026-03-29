from rest_framework import viewsets, status, filters
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.utils import timezone
from django.db.models import Q, Count, Avg, F, ExpressionWrapper, fields
from .models import SupportTicket
from .serializers import (
    SupportTicketSerializer, 
    CreateSupportTicketSerializer,
    AdminReplySerializer
)


class SupportTicketViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing support tickets
    """
    permission_classes = [IsAuthenticated]
    serializer_class = SupportTicketSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['ticket_number', 'subject', 'message']
    ordering_fields = ['created_at', 'priority', 'status']
    ordering = ['-created_at']
    pagination_class = None  # Disable pagination for this ViewSet
    
    def get_queryset(self):
        user = self.request.user
        
        # Admin can see all tickets
        if user.is_staff or user.is_superuser:
            queryset = SupportTicket.objects.all()
        else:
            # Regular users can only see their own tickets
            queryset = SupportTicket.objects.filter(user=user)
        
        # Filter by status
        status_filter = self.request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by priority
        priority_filter = self.request.query_params.get('priority', None)
        if priority_filter:
            queryset = queryset.filter(priority=priority_filter)
        
        # Filter by category
        category_filter = self.request.query_params.get('category', None)
        if category_filter:
            queryset = queryset.filter(category=category_filter)
        
        return queryset.select_related('user', 'admin_replied_by')
    
    def get_serializer_class(self):
        if self.action == 'create':
            return CreateSupportTicketSerializer
        return SupportTicketSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Create ticket with current user
        ticket = serializer.save(user=request.user)
        
        # Send confirmation email (optional - implement if needed)
        # send_ticket_confirmation_email(ticket)
        
        response_serializer = SupportTicketSerializer(ticket)
        return Response(
            {
                'message': 'Support ticket created successfully',
                'ticket': response_serializer.data
            },
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def reply(self, request, pk=None):
        """Admin endpoint to reply to a ticket"""
        ticket = self.get_object()
        serializer = AdminReplySerializer(data=request.data)
        
        if serializer.is_valid():
            ticket.admin_reply = serializer.validated_data['admin_reply']
            ticket.admin_replied_by = request.user
            ticket.admin_replied_at = timezone.now()
            
            # Update status if provided
            if 'status' in serializer.validated_data:
                ticket.status = serializer.validated_data['status']
            elif ticket.status == 'open':
                # Automatically move to in_progress when admin replies
                ticket.status = 'in_progress'
            
            ticket.save()
            
            # Send email notification to user (optional - implement if needed)
            # send_admin_reply_email(ticket)
            
            response_serializer = SupportTicketSerializer(ticket)
            return Response({
                'message': 'Reply sent successfully',
                'ticket': response_serializer.data
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['patch'], permission_classes=[IsAdminUser])
    def update_status(self, request, pk=None):
        """Admin endpoint to update ticket status"""
        ticket = self.get_object()
        new_status = request.data.get('status')
        
        if new_status not in dict(SupportTicket.STATUS_CHOICES):
            return Response(
                {'error': 'Invalid status'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        ticket.status = new_status
        ticket.save()
        
        response_serializer = SupportTicketSerializer(ticket)
        return Response({
            'message': 'Status updated successfully',
            'ticket': response_serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def my_tickets(self, request):
        """Get current user's tickets"""
        tickets = SupportTicket.objects.filter(user=request.user)
        
        # Apply filters
        status_filter = request.query_params.get('status')
        if status_filter:
            tickets = tickets.filter(status=status_filter)
        
        serializer = self.get_serializer(tickets, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], permission_classes=[IsAdminUser])
    def statistics(self, request):
        """Get support ticket statistics for admin dashboard"""
        tickets = SupportTicket.objects.all()
        
        # Count by status
        status_counts = tickets.values('status').annotate(count=Count('id'))
        
        # Count by priority
        priority_counts = tickets.values('priority').annotate(count=Count('id'))
        
        # Calculate average response time
        tickets_with_reply = tickets.filter(admin_replied_at__isnull=False)
        avg_response_time = None
        if tickets_with_reply.exists():
            # Calculate response time in hours
            response_times = []
            for ticket in tickets_with_reply:
                if ticket.response_time:
                    response_times.append(ticket.response_time)
            if response_times:
                avg_response_time = sum(response_times) / len(response_times)
        
        # Recent tickets
        recent_tickets = tickets[:10]
        recent_serializer = SupportTicketSerializer(recent_tickets, many=True)
        
        return Response({
            'total_tickets': tickets.count(),
            'status_breakdown': {item['status']: item['count'] for item in status_counts},
            'priority_breakdown': {item['priority']: item['count'] for item in priority_counts},
            'average_response_time_hours': round(avg_response_time, 2) if avg_response_time else None,
            'recent_tickets': recent_serializer.data
        })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def ticket_stats(request):
    """Get ticket statistics for current user"""
    user = request.user
    tickets = SupportTicket.objects.filter(user=user)
    
    return Response({
        'total': tickets.count(),
        'open': tickets.filter(status='open').count(),
        'in_progress': tickets.filter(status='in_progress').count(),
        'resolved': tickets.filter(status='resolved').count(),
        'closed': tickets.filter(status='closed').count(),
    })
