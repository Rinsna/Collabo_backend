from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.db import transaction
from .models import Campaign

@receiver(pre_save, sender=Campaign)
def handle_campaign_status_change(sender, instance, **kwargs):
    """
    Handle campaign status changes to 'completed'.
    Add campaign budget to company's pending payment balance.
    """
    if not instance.pk:
        # New campaign, skip
        return
    
    try:
        old_instance = Campaign.objects.get(pk=instance.pk)
    except Campaign.DoesNotExist:
        return
    
    # Check if status changed to 'completed' and payment hasn't been added yet
    if (old_instance.status != 'completed' and 
        instance.status == 'completed' and 
        not instance.payment_added_to_pending):
        
        # Add budget to company's pending payment
        company_profile = instance.company.company_profile
        
        with transaction.atomic():
            company_profile.pending_payment += instance.budget
            company_profile.save()
            
            # Mark that payment has been added to pending
            instance.payment_added_to_pending = True
            
            print(f"Campaign '{instance.title}' completed. Added ₹{instance.budget} to pending payment.")
            print(f"Company '{company_profile.company_name}' pending payment: ₹{company_profile.pending_payment}")
