from django.contrib import admin
from .models import Payment, Payout

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('collaboration', 'payer', 'payee', 'amount', 'platform_fee', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('collaboration__request__campaign__title', 'payer__username', 'payee__username')
    readonly_fields = ('platform_fee', 'net_amount')

@admin.register(Payout)
class PayoutAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username',)