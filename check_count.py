from landing.models import CatalogImage
with open("count_status.txt", "w") as f:
    f.write(str(CatalogImage.objects.count()))
