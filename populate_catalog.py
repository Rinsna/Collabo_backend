import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from landing.models import CatalogImage

if CatalogImage.objects.count() == 0:
    images = [
        "https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?w=600&h=800&fit=crop",
        "https://images.unsplash.com/photo-1529139574466-a303027c1d8b?w=600&h=800&fit=crop",
        "https://images.unsplash.com/photo-1483985988355-763728e1935b?w=600&h=800&fit=crop",
        "https://images.unsplash.com/photo-1550614000-4b95d466f111?w=600&h=800&fit=crop",
        "https://images.unsplash.com/photo-1525507119028-ed4c629a60a3?w=600&h=800&fit=crop",
    ]
    for i, img in enumerate(images):
        CatalogImage.objects.create(image_url=img, order=i)
    print("Catalog views created!")
