from rest_framework import serializers
from .models import HeroContent, HeroCard, CatalogImage

class HeroContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = HeroContent
        fields = '__all__'

class HeroCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = HeroCard
        fields = '__all__'

class CatalogImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = CatalogImage
        fields = '__all__'
