from django.db import models

class HeroContent(models.Model):
    badge_text = models.CharField(max_length=100, default="The New Standard for Influencer Marketing")
    title = models.CharField(max_length=200, default="Where Creators & Brands Innovate")
    subtitle = models.TextField(default="Discover, collaborate, and scale your reach. The all-in-one platform connecting authentic creators with world-class brands.")
    creator_button_text = models.CharField(max_length=50, default="Sign up as a Creator")
    brand_button_text = models.CharField(max_length=50, default="Sign up as a Brand")
    
    # Animated Text Section Content
    anim_text = models.TextField(default="Maximize Your {img1} Brand's\nGrowth and {img2}{img3}{img4} Skyrocket Sales\nby Leveraging the Potential\nof Creator Marketing")
    anim_image1 = models.TextField(blank=True, null=True, default="https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=400&h=200&fit=crop")
    anim_image2 = models.TextField(blank=True, null=True, default="https://images.unsplash.com/photo-1517841905240-472988babdf9?w=200&h=200&fit=crop")
    anim_image3 = models.TextField(blank=True, null=True, default="https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=200&h=200&fit=crop")
    anim_image4 = models.TextField(blank=True, null=True, default="https://images.unsplash.com/photo-1539571696357-5a69c17a67c6?w=200&h=200&fit=crop")
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Hero Content"

    def __str__(self):
        return self.title

class HeroCard(models.Model):
    CARD_SIZE_CHOICES = [
        ('small', 'Small (Badge)'),
        ('medium', 'Medium'),
        ('large', 'Large'),
    ]

    image_url = models.TextField(blank=True, null=True, help_text="URL for the card image. Leave blank for text-only badges.")
    label = models.CharField(max_length=50, blank=True, help_text="Main text shown on the card")
    
    background_color = models.CharField(max_length=50, default="#F3F4F6", help_text="Hex color or Tailwind bg- class")
    text_color = models.CharField(max_length=50, default="#000000", help_text="Hex color or Tailwind text- class")
    
    # Attachment/Overlapping Badge
    attachment_label = models.CharField(max_length=50, blank=True, help_text="Text for the overlapping small badge")
    attachment_bg_color = models.CharField(max_length=50, default="#FFFFFF", help_text="Background color of the attachment")
    attachment_text_color = models.CharField(max_length=50, default="#000000", help_text="Text color of the attachment")
    
    card_size = models.CharField(max_length=20, choices=CARD_SIZE_CHOICES, default='medium')
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.label or f"Card {self.id}"

class CatalogImage(models.Model):
    image_url = models.TextField(help_text="URL for the catalog image")
    
    # Typography content for the flip cards
    title = models.CharField(max_length=100, default="THE NEW EDIT")
    subtitle = models.CharField(max_length=100, default="URBAN")
    accent_text = models.CharField(max_length=100, default="MODERN MINIMALISM")
    tagline = models.CharField(max_length=100, default="Discover AW24 Collection")
    
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.title} - {self.subtitle} ({self.order})"
