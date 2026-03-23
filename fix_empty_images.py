import os
import django

# Setup django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'influencer_platform.settings')
django.setup()

from landing.models import CatalogImage

# Identify and fix empty image URLs
empty_images = CatalogImage.objects.filter(image_url__isnull=True) | CatalogImage.objects.filter(image_url='')
count = empty_images.count()

fallbacks = [
    "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=800&q=80",
    "https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?w=800&q=80",
    "https://images.unsplash.com/photo-1531746020798-e6953c6e8e04?w=800&q=80",
    "https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=800&q=80",
    "https://images.unsplash.com/photo-1552374196-c4e7ffc6e126?w=800&q=80"
]

for i, obj in enumerate(empty_images):
    obj.image_url = fallbacks[i % len(fallbacks)]
    obj.save()

print(f"Fixed {count} empty catalog images.")
