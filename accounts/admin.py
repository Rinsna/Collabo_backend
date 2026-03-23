from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils import timezone
from .models import User, InfluencerProfile, CompanyProfile

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'username', 'user_type', 'approval_status', 'is_approved', 'is_verified', 'is_active', 'created_at')
    list_filter = ('user_type', 'approval_status', 'is_approved', 'is_verified', 'is_active', 'created_at')
    search_fields = ('email', 'username')
    ordering = ('-created_at',)
    actions = ['approve_influencers', 'reject_influencers']
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('user_type', 'phone', 'is_verified')}),
        ('Approval System', {'fields': ('is_approved', 'approval_status', 'approved_at', 'approved_by', 'rejection_reason')}),
    )
    
    readonly_fields = ('approved_at', 'approved_by', 'created_at')
    
    def approve_influencers(self, request, queryset):
        """Admin action to approve selected influencers"""
        influencers = queryset.filter(user_type='influencer')
        count = 0
        for user in influencers:
            user.is_approved = True
            user.approval_status = 'approved'
            user.approved_at = timezone.now()
            user.approved_by = request.user
            user.rejection_reason = ''
            user.save()
            count += 1
        
        self.message_user(request, f'{count} influencer(s) approved successfully.')
    approve_influencers.short_description = 'Approve selected influencers'
    
    def reject_influencers(self, request, queryset):
        """Admin action to reject selected influencers"""
        influencers = queryset.filter(user_type='influencer')
        count = 0
        for user in influencers:
            user.is_approved = False
            user.approval_status = 'rejected'
            user.approved_at = None
            user.approved_by = None
            user.save()
            count += 1
        
        self.message_user(request, f'{count} influencer(s) rejected.')
    reject_influencers.short_description = 'Reject selected influencers'

class InfluencerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'category', 'followers_count', 'engagement_rate', 'rate_per_post', 'get_preferred_platforms', 'get_approval_status')
    list_filter = ('category', 'preferred_platforms', 'user__approval_status')
    search_fields = ('user__username', 'user__email', 'bio')
    raw_id_fields = ('user',)
    
    def get_preferred_platforms(self, obj):
        return ', '.join(obj.preferred_platforms) if obj.preferred_platforms else 'None'
    get_preferred_platforms.short_description = 'Preferred Platforms'
    
    def get_approval_status(self, obj):
        return obj.user.approval_status
    get_approval_status.short_description = 'Approval Status'

class CompanyProfileAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'user', 'industry')
    list_filter = ('industry',)
    search_fields = ('company_name', 'user__username', 'user__email')
    raw_id_fields = ('user',)

admin.site.register(InfluencerProfile, InfluencerProfileAdmin)
admin.site.register(CompanyProfile, CompanyProfileAdmin)