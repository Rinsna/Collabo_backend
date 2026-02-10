from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, InfluencerProfile, CompanyProfile

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'username', 'user_type', 'is_verified', 'is_active', 'created_at')
    list_filter = ('user_type', 'is_verified', 'is_active', 'created_at')
    search_fields = ('email', 'username')
    ordering = ('-created_at',)
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('user_type', 'phone', 'is_verified')}),
    )

class InfluencerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'category', 'followers_count', 'engagement_rate', 'rate_per_post', 'get_preferred_platforms')
    list_filter = ('category', 'preferred_platforms')
    search_fields = ('user__username', 'user__email', 'bio')
    raw_id_fields = ('user',)
    
    def get_preferred_platforms(self, obj):
        return ', '.join(obj.preferred_platforms) if obj.preferred_platforms else 'None'
    get_preferred_platforms.short_description = 'Preferred Platforms'

class CompanyProfileAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'user', 'industry')
    list_filter = ('industry',)
    search_fields = ('company_name', 'user__username', 'user__email')
    raw_id_fields = ('user',)

admin.site.register(InfluencerProfile, InfluencerProfileAdmin)
admin.site.register(CompanyProfile, CompanyProfileAdmin)