from django.db import models
from django.conf import settings
import uuid


class SupportTicket(models.Model):
    """
    Support ticket model for handling user support requests
    """
    CATEGORY_CHOICES = [
        ('technical', 'Technical'),
        ('payment', 'Payment'),
        ('campaign', 'Campaign'),
        ('account', 'Account'),
        ('other', 'Other'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]
    
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    ]
    
    # Unique ticket identifier
    ticket_number = models.CharField(max_length=20, unique=True, editable=False)
    
    # User information
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='support_tickets'
    )
    
    # Ticket details
    subject = models.CharField(max_length=255)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    message = models.TextField()
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    
    # Admin response
    admin_reply = models.TextField(blank=True, null=True)
    admin_replied_at = models.DateTimeField(blank=True, null=True)
    admin_replied_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='admin_ticket_replies'
    )
    
    # Optional screenshot
    screenshot = models.ImageField(upload_to='support_screenshots/', blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['priority', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.ticket_number} - {self.subject}"
    
    def save(self, *args, **kwargs):
        if not self.ticket_number:
            # Generate unique ticket number
            self.ticket_number = self.generate_ticket_number()
        super().save(*args, **kwargs)
    
    def generate_ticket_number(self):
        """Generate a unique ticket number in format: TKT-XXXXXX"""
        while True:
            ticket_num = f"TKT-{uuid.uuid4().hex[:6].upper()}"
            if not SupportTicket.objects.filter(ticket_number=ticket_num).exists():
                return ticket_num
    
    @property
    def response_time(self):
        """Calculate response time in hours"""
        if self.admin_replied_at:
            delta = self.admin_replied_at - self.created_at
            return round(delta.total_seconds() / 3600, 2)
        return None
