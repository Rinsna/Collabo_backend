from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LandingContentViewSet

router = DefaultRouter()
router.register(r'content', LandingContentViewSet, basename='landing-content')

urlpatterns = [
    path('', include(router.urls)),
]
