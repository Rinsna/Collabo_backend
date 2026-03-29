from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAdminUser
from .models import HeroContent, HeroCard, CatalogImage
from .serializers import HeroContentSerializer, HeroCardSerializer, CatalogImageSerializer

class LandingContentViewSet(viewsets.ViewSet):
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAdminUser()]

    def list(self, request):
        hero_content = HeroContent.objects.filter(is_active=True).first()
        hero_cards = HeroCard.objects.filter(is_active=True)
        catalog_images = CatalogImage.objects.filter(is_active=True).order_by('order')
        
        return Response({
            'hero': HeroContentSerializer(hero_content).data if hero_content else None,
            'cards': HeroCardSerializer(hero_cards, many=True).data,
            'catalog_images': CatalogImageSerializer(catalog_images, many=True).data
        })

    @action(detail=False, methods=['post'], url_path='update-hero')
    def update_hero(self, request):
        hero_content = HeroContent.objects.filter(is_active=True).first()
        if not hero_content:
            serializer = HeroContentSerializer(data=request.data)
        else:
            serializer = HeroContentSerializer(hero_content, data=request.data, partial=True)
            
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], url_path='add-card')
    def add_card(self, request):
        serializer = HeroCardSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['patch', 'delete'], url_path='manage-card')
    def manage_card(self, request, pk=None):
        try:
            card = HeroCard.objects.get(pk=pk)
        except HeroCard.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if request.method == 'DELETE':
            card.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
            
        serializer = HeroCardSerializer(card, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], url_path='add-catalog-image')
    def add_catalog_image(self, request):
        serializer = CatalogImageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['patch', 'delete'], url_path='manage-catalog-image')
    def manage_catalog_image(self, request, pk=None):
        try:
            image = CatalogImage.objects.get(pk=pk)
        except CatalogImage.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if request.method == 'DELETE':
            image.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
            
        serializer = CatalogImageSerializer(image, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
