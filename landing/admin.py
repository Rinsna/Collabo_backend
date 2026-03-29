from django.contrib import admin
from .models import HeroContent, HeroCard, CatalogImage

@admin.register(HeroContent)
class HeroContentAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_active', 'updated_at')
    
    def has_add_permission(self, request):
        # Only allow one active hero content
        if self.model.objects.count() >= 1:
            return False
        return super().has_add_permission(request)

@admin.register(HeroCard)
class HeroCardAdmin(admin.ModelAdmin):
    list_display = ('label', 'card_size', 'is_active', 'order')
    list_editable = ('is_active', 'order', 'card_size')
    list_filter = ('is_active', 'card_size')
    fieldsets = (
        (None, {
            'fields': ('label', 'image_url', 'card_size', 'order', 'is_active')
        }),
        ('Styling', {
            'fields': ('background_color', 'text_color'),
            'description': 'Use Hex codes (e.g. #FF0000) or Tailwind classes.'
        }),
        ('Attachment (Overlapping Badge)', {
            'fields': ('attachment_label', 'attachment_bg_color', 'attachment_text_color'),
            'classes': ('collapse',),
        }),
    )
@admin.register(CatalogImage)
class CatalogImageAdmin(admin.ModelAdmin):
    list_display = ('title', 'subtitle', 'is_active', 'order')
    list_editable = ('is_active', 'order')
    list_filter = ('is_active',)
    search_fields = ('title', 'subtitle', 'accent_text', 'tagline')
    fieldsets = (
        (None, {
            'fields': ('image_url', 'order', 'is_active')
        }),
        ('Typography Overlay', {
            'fields': ('title', 'subtitle', 'accent_text', 'tagline'),
            'description': 'Text that appears over the images in the catalog stack.'
        }),
    )
