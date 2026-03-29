from django.contrib import admin
from .models import SupportTicket


@admin.register(SupportTicket)
class SupportTicketAdmin(admin.ModelAdmin):
    list_display = ['ticket_number', 'subject', 'user', 'category', 'priority', 'status', 'created_at']
    list_filter = ['status', 'priority', 'category', 'created_at']
    search_fields = ['ticket_number', 'subject', 'user__username', 'user__email']
    readonly_fields = ['ticket_number', 'created_at', 'updated_at', 'response_time']
    
    fieldsets = (
        ('Ticket Information', {
            'fields': ('ticket_number', 'user', 'subject', 'category', 'priority', 'status')
        }),
        ('Message', {
            'fields': ('message', 'screenshot')
        }),
        ('Admin Response', {
            'fields': ('admin_reply', 'admin_replied_by', 'admin_replied_at')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'response_time')
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if change and 'admin_reply' in form.changed_data and obj.admin_reply:
            # Set admin reply metadata
            from django.utils import timezone
            if not obj.admin_replied_at:
                obj.admin_replied_at = timezone.now()
            if not obj.admin_replied_by:
                obj.admin_replied_by = request.user
        super().save_model(request, obj, form, change)
