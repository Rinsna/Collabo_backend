from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SupportTicketViewSet, ticket_stats

router = DefaultRouter()
router.register(r'tickets', SupportTicketViewSet, basename='support-ticket')

urlpatterns = [
    path('', include(router.urls)),
    path('stats/', ticket_stats, name='ticket-stats'),
]
