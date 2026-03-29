import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'influencer_platform.settings')
django.setup()

from landing.models import CatalogImage

CatalogImage.objects.all().delete()
data = [
    {
        "url": "https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?w=600&h=800&fit=crop",
        "title": "SPRING COLLECTION",
        "subtitle": "PASTELS",
        "accent": "SOFT TEXTURE",
        "tagline": "Discover the 2024 Bloom Series"
    },
    {
        "url": "https://images.unsplash.com/photo-1529139574466-a303027c1d8b?w=600&h=800&fit=crop",
        "title": "URBAN NOMAD",
        "subtitle": "CONCRETE",
        "accent": "RUGGED DURABILITY",
        "tagline": "Engineered for City Life"
    },
    {
        "url": "https://images.unsplash.com/photo-1483985988355-763728e1935b?w=600&h=800&fit=crop",
        "title": "LUXE EDIT",
        "subtitle": "GOLDEN",
        "accent": "PURE ELEGANCE",
        "tagline": "Exquisite Evening Wear"
    },
    {
        "url": "https://images.unsplash.com/photo-1550614000-4b95d466f111?w=600&h=800&fit=crop",
        "title": "MINIMALIST",
        "subtitle": "MONO",
        "accent": "SIMPLE LINES",
        "tagline": "The Beauty of Less"
    },
    {
        "url": "https://images.unsplash.com/photo-1525507119028-ed4c629a60a3?w=600&h=800&fit=crop",
        "title": "STREET SOUL",
        "subtitle": "KICKZ",
        "accent": "VIBRANT ENERGY",
        "tagline": "Limited Edition Drops"
    },
    {
        "url": "https://images.unsplash.com/photo-1539109136881-3be0616acf4b?w=600&h=800&fit=crop",
        "title": "INDIE STYLE",
        "subtitle": "RETRO",
        "accent": "LO-FI VIBES",
        "tagline": "Vintage Cuts for Today"
    },
    {
        "url": "https://images.unsplash.com/photo-1496747611176-843222e1e57c?w=600&h=800&fit=crop",
        "title": "BOHEMIAN",
        "subtitle": "SUMMER",
        "accent": "LIGHT FLOW",
        "tagline": "Wild Hearts Run Free"
    },
    {
        "url": "https://images.unsplash.com/photo-1512436991641-6745cdb1723f?w=600&h=800&fit=crop",
        "title": "SOPHISTICATE",
        "subtitle": "NOIR",
        "accent": "BOLD DARK",
        "tagline": "Darkness Redefined"
    },
    {
        "url": "https://images.unsplash.com/photo-1509631179647-0177331693ae?w=600&h=800&fit=crop",
        "title": "AURA SERIES",
        "subtitle": "GLOW",
        "accent": "SOFT LIGHT",
        "tagline": "Radiance from Within"
    },
    {
        "url": "https://images.unsplash.com/photo-1502716119720-b23a93e5fe1b?w=600&h=800&fit=crop",
        "title": "EDITORIAL",
        "subtitle": "VOGUE",
        "accent": "HIGH FASHION",
        "tagline": "Front Page Exclusives"
    },
    {
        "url": "https://images.unsplash.com/photo-1492707892479-7bc8d5a4ee93?w=600&h=800&fit=crop",
        "title": "AVANT GARDE",
        "subtitle": "STRUCTURE",
        "accent": "GEO CUTS",
        "tagline": "Bold Architectural Wear"
    },
    {
        "url": "https://images.unsplash.com/photo-1518766185805-4c070f7d5498?w=600&h=800&fit=crop",
        "title": "NOSTALGIA",
        "subtitle": "DENIM",
        "accent": "BLUE WASH",
        "tagline": "Timeless Classics"
    },
    {
        "url": "https://images.unsplash.com/photo-1523381210434-271e8be1f52b?w=600&h=800&fit=crop",
        "title": "PURE LUXE",
        "subtitle": "SILK",
        "accent": "LIQUID TEXTURE",
        "tagline": "Refined Comfort"
    },
    {
        "url": "https://images.unsplash.com/photo-1524250502761-1ac6f2e30d43?w=600&h=800&fit=crop",
        "title": "OUTDOOR VIBE",
        "subtitle": "TRAIL",
        "accent": "EARTH TONES",
        "tagline": "Nature Meets Gear"
    },
    {
        "url": "https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?w=600&h=800&fit=crop",
        "title": "FINALE EDIT",
        "subtitle": "ICED",
        "accent": "COOL TINTS",
        "tagline": "Season Closer"
    },
    {
        "url": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=600&h=800&fit=crop",
        "title": "PORTRAIT I",
        "subtitle": "STUDIO",
        "accent": "SOFT SHADOWS",
        "tagline": "The Art of the Face"
    },
    {
        "url": "https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?w=600&h=800&fit=crop",
        "title": "MENSWEAR",
        "subtitle": "TAILORED",
        "accent": "SHARP CUTS",
        "tagline": "Modern Gentleman"
    },
    {
        "url": "https://images.unsplash.com/photo-1531746020798-e6953c6e8e04?w=600&h=800&fit=crop",
        "title": "FUTURISM",
        "subtitle": "NEON",
        "accent": "GLOW TECH",
        "tagline": "Beyond Tomorrow"
    },
    {
        "url": "https://images.unsplash.com/photo-1534773728080-33d31da27ae5?w=600&h=800&fit=crop",
        "title": "STREET II",
        "subtitle": "CONCRETE",
        "accent": "RAW EDGE",
        "tagline": "Sidewalk Stories"
    },
    {
        "url": "https://images.unsplash.com/photo-1524504388940-b1c1722653e1?w=600&h=800&fit=crop",
        "title": "FASHION ART",
        "subtitle": "AVANT",
        "accent": "BOLD MOVES",
        "tagline": "Expressive Style"
    },
    {
        "url": "https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=600&h=800&fit=crop",
        "title": "GLAMOUR",
        "subtitle": "ELEGANCE",
        "accent": "SILK TOUCH",
        "tagline": "Timeless Beauty"
    },
    {
        "url": "https://images.unsplash.com/photo-1519345182560-3f2917c472ef?w=600&h=800&fit=crop",
        "title": "MAVERICK",
        "subtitle": "BOLD",
        "accent": "REBEL SPIRIT",
        "tagline": "Fearless Fashion"
    },
    {
        "url": "https://images.unsplash.com/photo-1552374196-c4e7ffc6e126?w=600&h=800&fit=crop",
        "title": "MUSE SERIES",
        "subtitle": "INSPIRE",
        "accent": "SOULFUL",
        "tagline": "Capturing the Essence"
    },
    {
        "url": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=600&h=800&fit=crop",
        "title": "COLASSAL",
        "subtitle": "GRAND",
        "accent": "SCALE",
        "tagline": "Larger Than Life"
    },
]

for i, item in enumerate(data):
    CatalogImage.objects.create(
        image_url=item["url"],
        title=item["title"],
        subtitle=item["subtitle"],
        accent_text=item["accent"],
        tagline=item["tagline"],
        order=i
    )

print(f"DONE, created {CatalogImage.objects.count()} images.")
