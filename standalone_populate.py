import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'influencer_platform.settings')
django.setup()

from landing.models import CatalogImage

CatalogImage.objects.all().delete()
images = [
    "https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?w=800&q=80",
    "https://images.unsplash.com/photo-1529139574466-a303027c1d8b?w=800&q=80",
    "https://images.unsplash.com/photo-1483985988355-763728e1935b?w=800&q=80",
    "https://images.unsplash.com/photo-1550614000-4b95d466f111?w=800&q=80",
    "https://images.unsplash.com/photo-1525507119028-ed4c629a60a3?w=800&q=80",
]
for i, url in enumerate(images):
    CatalogImage.objects.create(image_url=url, order=i)

print(f"CREATED {CatalogImage.objects.count()} IMAGES")
