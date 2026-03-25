from django.db import migrations

def seed_landing_data(apps, schema_editor):
    HeroContent = apps.get_model('landing', 'HeroContent')
    HeroCard = apps.get_model('landing', 'HeroCard')
    CatalogImage = apps.get_model('landing', 'CatalogImage')

    # 1. Seed Hero Content
    if not HeroContent.objects.exists():
        HeroContent.objects.create(
            title="Where Teams Connect,\nCollaborate, and Create",
            subtitle="Partner with creators who turn content into conversions and help brands grow through real-world performance.",
            creator_button_text="Sign up as a Creator",
            brand_button_text="Sign up as a Brand"
        )

    # 2. Seed Hero Cards (Marquee)
    if not HeroCard.objects.exists():
        cards_data = [
            {"label": "FASHION", "image_url": "https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?w=600&h=800&fit=crop", "card_size": "large", "background_color": "#FDF2F8"},
            {"label": "LIFESTYLE", "image_url": "https://images.unsplash.com/photo-1534126416832-a88fdf2911c2?w=600&h=800&fit=crop", "card_size": "medium", "background_color": "#F5F3FF"},
            {"label": "CREATIVITY", "image_url": "https://images.unsplash.com/photo-1524504388940-b1c1722653e1?w=600&h=800&fit=crop", "card_size": "small", "background_color": "#F0F9FF"},
            {"label": "GROWTH", "image_url": "https://images.unsplash.com/photo-1529139513055-07f9f27e555e?w=600&h=800&fit=crop", "card_size": "large", "background_color": "#ECFDF5"},
            {"label": "BEAUTY", "image_url": "https://images.unsplash.com/photo-1512496015851-a90fb38ba796?w=600&h=800&fit=crop", "card_size": "medium", "background_color": "#FFF7ED"},
            {"label": "TECH", "image_url": "https://images.unsplash.com/photo-1519389950473-47ba0277781c?w=600&h=800&fit=crop", "card_size": "small", "background_color": "#F8FAFC"},
        ]
        for i, data in enumerate(cards_data):
            HeroCard.objects.create(order=i, **data)

    # 3. Seed Catalog Images (Flip Cards)
    if not CatalogImage.objects.exists():
        catalog_data = [
            {"title": "STREET STYLE", "subtitle": "URBAN", "image_url": "https://images.unsplash.com/photo-1509631179647-0177331693ae?w=800&q=80"},
            {"title": "MINIMALIST", "subtitle": "ESSENTIAL", "image_url": "https://images.unsplash.com/photo-1434389677669-e08b4cac3105?w=800&q=80"},
            {"title": "LUXURY", "subtitle": "PREMIUM", "image_url": "https://images.unsplash.com/photo-1445205174273-59396b27d34e?w=800&q=80"},
            {"title": "VINTAGE", "subtitle": "RETRO", "image_url": "https://images.unsplash.com/photo-1520243947988-b7b79f7873e9?w=800&q=80"},
        ]
        for i, data in enumerate(catalog_data):
            CatalogImage.objects.create(order=i, **data)

def reverse_seed(apps, schema_editor):
    pass # No need to delete on reverse

class Migration(migrations.Migration):
    dependencies = [
        ('landing', '0007_catalogimage_accent_text_catalogimage_subtitle_and_more'),
    ]

    operations = [
        migrations.RunPython(seed_landing_data, reverse_seed),
    ]
