from rest_framework import serializers
from .models import Campaign, CollaborationRequest, DirectCollaborationRequest, Collaboration, Review
from accounts.serializers import UserSerializer

class CampaignSerializer(serializers.ModelSerializer):
    company_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Campaign
        fields = '__all__'
        read_only_fields = ('company',)
    
    def get_company_name(self, obj):
        try:
            return obj.company.company_profile.company_name
        except AttributeError:
            return obj.company.username

class DirectCollaborationRequestSerializer(serializers.ModelSerializer):
    influencer_username = serializers.CharField(source='influencer.username', read_only=True)
    influencer_profile = serializers.SerializerMethodField()
    company_name = serializers.SerializerMethodField()
    campaign_title = serializers.SerializerMethodField()
    
    class Meta:
        model = DirectCollaborationRequest
        fields = '__all__'
        read_only_fields = ('company', 'created_at', 'updated_at')
    
    def get_influencer_profile(self, obj):
        try:
            profile = obj.influencer.influencer_profile
            return {
                'followers_count': profile.followers_count,
                'category': profile.category,
                'engagement_rate': profile.engagement_rate,
                'rate_per_post': profile.rate_per_post
            }
        except AttributeError:
            return None
    
    def get_company_name(self, obj):
        try:
            return obj.company.company_profile.company_name
        except AttributeError:
            return obj.company.username
    
    def get_campaign_title(self, obj):
        return obj.campaign_details.get('title', 'Untitled Campaign')
    
    def create(self, validated_data):
        # Set the company from the request user
        validated_data['company'] = self.context['request'].user
        return super().create(validated_data)

class CollaborationRequestSerializer(serializers.ModelSerializer):
    campaign_title = serializers.CharField(source='campaign.title', read_only=True)
    influencer_username = serializers.CharField(source='influencer.username', read_only=True)
    company_name = serializers.SerializerMethodField()
    
    class Meta:
        model = CollaborationRequest
        fields = '__all__'
        read_only_fields = ('company', 'influencer', 'created_at', 'updated_at')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make campaign read-only for updates, but allow it for creation
        if self.instance is not None:  # This is an update
            self.fields['campaign'].read_only = True
            self.fields['proposed_rate'].required = False
    
    def get_company_name(self, obj):
        try:
            return obj.company.company_profile.company_name
        except AttributeError:
            return obj.company.username
    
    def update(self, instance, validated_data):
        # Only allow updating certain fields
        allowed_fields = ['status', 'message', 'proposed_rate', 'rejection_reason']
        for field in allowed_fields:
            if field in validated_data:
                setattr(instance, field, validated_data[field])
        instance.save()
        return instance

class CollaborationSerializer(serializers.ModelSerializer):
    campaign_title = serializers.SerializerMethodField()
    influencer_username = serializers.SerializerMethodField()
    company_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Collaboration
        fields = '__all__'
    
    def get_campaign_title(self, obj):
        if obj.request:
            return obj.request.campaign.title
        elif obj.direct_request:
            return obj.direct_request.campaign_details.get('title', 'Direct Collaboration')
        return 'Unknown Campaign'
    
    def get_influencer_username(self, obj):
        if obj.request:
            return obj.request.influencer.username
        elif obj.direct_request:
            return obj.direct_request.influencer.username
        return 'Unknown Influencer'
    
    def get_company_name(self, obj):
        try:
            if obj.request:
                return obj.request.company.company_profile.company_name
            elif obj.direct_request:
                return obj.direct_request.company.company_profile.company_name
        except AttributeError:
            if obj.request:
                return obj.request.company.username
            elif obj.direct_request:
                return obj.direct_request.company.username
        return 'Unknown Company'

class ReviewSerializer(serializers.ModelSerializer):
    reviewer_username = serializers.CharField(source='reviewer.username', read_only=True)
    reviewee_username = serializers.CharField(source='reviewee.username', read_only=True)
    
    class Meta:
        model = Review
        fields = '__all__'
        read_only_fields = ('reviewer',)