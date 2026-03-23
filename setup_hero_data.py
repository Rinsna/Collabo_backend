import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'influencer_platform.settings')
django.setup()

from landing.models import HeroContent, HeroCard, CatalogImage

def setup_hero():
    # Hero Content
    hero, created = HeroContent.objects.get_or_create(
        id=1,
        defaults={
            'badge_text': 'The New Standard for Influencer Marketing',
            'title': 'Where {Teams} Connect,\nCollaborate, and Create',
            'subtitle': 'Discover, collaborate, and scale your reach. The all-in-one platform connecting authentic creators with world-class brands.',
            'creator_button_text': 'Sign up as a Creator',
            'brand_button_text': 'Sign up as a Brand',
            'anim_text': "Maximize Your {img1} Brand's\nGrowth and {img2}{img3}{img4} {Skyrocket Sales}\nby Leveraging the Potential\nof {Creator Marketing}"
        }
    )
    if not created:
        hero.title = 'Where {Teams} Connect,\nCollaborate, and Create'
        hero.subtitle = 'Discover, collaborate, and scale your reach. The all-in-one platform connecting authentic creators with world-class brands.'
        hero.anim_text = "Maximize Your {img1} Brand's\nGrowth and {img2}{img3}{img4} {Skyrocket Sales}\nby Leveraging the Potential\nof {Creator Marketing}"
        hero.save()
        print("Updated Hero Content")
    else:
        print("Created Hero Content")

    # Hero Cards
    cards_data = [
        {'label': 'XLASH', 'image_url': 'https://images.unsplash.com/photo-1552046122-03184de85e08?q=80&w=600&h=800&auto=format&fit=crop', 'background_color': '#FFFFFF'},
        {'label': 'SPACENK', 'image_url': 'https://images.unsplash.com/photo-1612817288484-6f916006741a?q=80&w=600&h=800&auto=format&fit=crop', 'background_color': '#FFFFFF'},
        {'label': 'ARKET', 'image_url': 'https://images.unsplash.com/photo-1483985988355-763728e1935b?q=80&w=600&h=800&auto=format&fit=crop', 'background_color': '#FFFFFF'},
        {'label': 'DYSON', 'image_url': 'https://images.unsplash.com/photo-1523275335684-37898b6baf30?q=80&w=600&h=800&auto=format&fit=crop', 'background_color': '#FFFFFF'},
        {'label': 'KICKS', 'image_url': 'https://images.unsplash.com/photo-1512446815102-45a8276f9272?q=80&w=600&h=800&auto=format&fit=crop', 'background_color': '#FFFFFF'},
        {'label': 'WEEKDAY', 'image_url': 'https://images.unsplash.com/photo-1521572267360-ee0c2909d518?q=80&w=600&h=800&auto=format&fit=crop', 'background_color': '#FFFFFF'},
        {'label': 'ADIDAS', 'image_url': 'https://images.unsplash.com/photo-1518002171953-a080ee817e1f?q=80&w=600&h=800&auto=format&fit=crop', 'background_color': '#FFFFFF'},
        {'label': 'NIKE', 'image_url': 'https://images.unsplash.com/photo-1542291026-7eec264c27ff?q=80&w=600&h=800&auto=format&fit=crop', 'background_color': '#FFFFFF'},
    ]

    for i, data in enumerate(cards_data):
        card, created = HeroCard.objects.get_or_create(
            label=data['label'],
            defaults={'image_url': data['image_url'], 'order': i, 'background_color': data.get('background_color', '#FFFFFF'), 'attachment_label': data.get('attachment_label', '')}
        )
        if not created:
            card.image_url = data['image_url']
            card.background_color = data.get('background_color', '#FFFFFF')
            card.attachment_label = data.get('attachment_label', '')
            card.save()
            print(f"Updated card: {data['label']}")
        else:
            print(f"Created card: {data['label']}")

    # Catalog Images
    catalog_data = [
        {'title': 'THE NEW EDIT', 'subtitle': 'URBAN', 'accent_text': 'MODERN MINIMALISM', 'tagline': 'Discover AW24 Collection', 'image_url': 'https://images.unsplash.com/photo-1534126416832-a88fdf2911c2?w=800&q=80'},
        {'title': 'STREET STYLE', 'subtitle': 'VIBE', 'accent_text': 'CORE ESSENTIALS', 'tagline': 'Summer Series 2024', 'image_url': 'https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?w=600&h=800&auto=format&fit=crop'},
        {'title': 'LUXE WEAR', 'subtitle': 'PARIS', 'accent_text': 'TIMELESS LUXURY', 'tagline': 'Exclusive Access Only', 'image_url': 'https://images.unsplash.com/photo-1490481651871-ab68de25d43d?w=800&q=80'},
        {'title': 'TECH FIT', 'subtitle': 'NEXT', 'accent_text': 'HIGH PERFORMANCE', 'tagline': 'Built for Athletes', 'image_url': 'https://images.unsplash.com/photo-1539109136881-3be0616acd4b?w=800&q=80'},
    ]

    for i, data in enumerate(catalog_data):
        img, created = CatalogImage.objects.get_or_create(
            title=data['title'],
            defaults={'image_url': data['image_url'], 'subtitle': data['subtitle'], 'accent_text': data['accent_text'], 'tagline': data['tagline'], 'order': i}
        )
        if not created:
            img.image_url = data['image_url']
            img.subtitle = data['subtitle']
            img.save()
            print(f"Updated catalog: {data['title']}")
        else:
            print(f"Created catalog: {data['title']}")

if __name__ == '__main__':
    setup_hero()
