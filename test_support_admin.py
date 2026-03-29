#!/usr/bin/env python
"""
Test script to verify support tickets are accessible
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'influencer_platform.settings')
django.setup()

from support.models import SupportTicket
from django.contrib.admin.sites import site

# Check if SupportTicket is registered in admin
print("=" * 60)
print("SUPPORT TICKET ADMIN VERIFICATION")
print("=" * 60)

# Check model registration
if SupportTicket in site._registry:
    print("✅ SupportTicket is registered in Django admin")
    admin_class = site._registry[SupportTicket]
    print(f"   Admin class: {admin_class.__class__.__name__}")
else:
    print("❌ SupportTicket is NOT registered in Django admin")

# Check tickets in database
tickets = SupportTicket.objects.all()
print(f"\n📊 Total tickets in database: {tickets.count()}")

if tickets.exists():
    print("\n📋 Ticket List:")
    print("-" * 60)
    for ticket in tickets:
        print(f"   {ticket.ticket_number} | {ticket.subject[:40]}")
        print(f"   Status: {ticket.status} | Priority: {ticket.priority}")
        print(f"   User: {ticket.user.username} | Created: {ticket.created_at.strftime('%Y-%m-%d %H:%M')}")
        print("-" * 60)
else:
    print("   No tickets found")

print("\n🔗 Admin URL: http://localhost:8000/admin/support/supportticket/")
print("=" * 60)
