from rest_framework import serializers
from .models import SupportTicket
from accounts.serializers import UserSerializer


class SupportTicketSerializer(serializers.ModelSerializer):
    user_details = UserSerializer(source='user', read_only=True)
    response_time = serializers.ReadOnlyField()
    
    class Meta:
        model = SupportTicket
        fields = [
            'id', 'ticket_number', 'user', 'user_details', 'subject', 
            'category', 'message', 'priority', 'status', 'admin_reply',
            'admin_replied_at', 'admin_replied_by', 'screenshot',
            'created_at', 'updated_at', 'response_time'
        ]
        read_only_fields = ['ticket_number', 'user', 'created_at', 'updated_at', 'admin_replied_at', 'admin_replied_by']


class CreateSupportTicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupportTicket
        fields = ['subject', 'category', 'message', 'priority', 'screenshot']
    
    def validate_subject(self, value):
        if len(value.strip()) < 5:
            raise serializers.ValidationError("Subject must be at least 5 characters long.")
        return value
    
    def validate_message(self, value):
        if len(value.strip()) < 10:
            raise serializers.ValidationError("Message must be at least 10 characters long.")
        return value


class AdminReplySerializer(serializers.Serializer):
    admin_reply = serializers.CharField(required=True)
    status = serializers.ChoiceField(
        choices=SupportTicket.STATUS_CHOICES,
        required=False
    )
    
    def validate_admin_reply(self, value):
        if len(value.strip()) < 10:
            raise serializers.ValidationError("Reply must be at least 10 characters long.")
        return value
