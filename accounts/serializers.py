from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User, InfluencerProfile, CompanyProfile

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ('email', 'username', 'password', 'password_confirm', 'user_type', 'phone')
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match")
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user

class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()
    
    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        
        if email and password:
            user = authenticate(username=email, password=password)
            if not user:
                raise serializers.ValidationError('Invalid credentials')
            if not user.is_active:
                raise serializers.ValidationError('User account is disabled')
            attrs['user'] = user
            return attrs
        else:
            raise serializers.ValidationError('Must include email and password')

class InfluencerProfileSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    preferred_platforms_display = serializers.SerializerMethodField()
    
    # Override to accept both URLs and base64 data
    profile_image = serializers.CharField(allow_blank=True, required=False)
    
    class Meta:
        model = InfluencerProfile
        fields = [
            'id', 'user', 'user_email', 'username', 'bio', 'category', 
            'preferred_platforms', 'preferred_platforms_display',
            'followers_count', 'engagement_rate',
            'rate_per_post', 'rate_per_story', 'rate_per_reel', 'rate_per_video',
            'instagram_handle', 'youtube_channel',
            'profile_image', 'portfolio_images', 'portfolio_videos', 'website_url',
            'latest_product_review_link', 'latest_product_review_cover',
            'latest_product_review_views', 'latest_product_review_likes',
            'most_viewed_content_link', 'most_viewed_content_cover',
            'most_viewed_content_views', 'most_viewed_content_likes',
            'location', 'languages',
            'created_at', 'updated_at'
        ]
        read_only_fields = ('user', 'created_at', 'updated_at')
    
    def validate(self, attrs):
        # Remove any TikTok/Twitter fields if they somehow get sent
        attrs.pop('tiktok_handle', None)
        attrs.pop('twitter_handle', None)
        return attrs
    
    def get_preferred_platforms_display(self, obj):
        """Return human-readable platform names"""
        platform_choices = dict(InfluencerProfile.SOCIAL_MEDIA_PLATFORMS)
        return [platform_choices.get(platform, platform) for platform in obj.preferred_platforms]

class CompanyProfileSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = CompanyProfile
        fields = '__all__'
        read_only_fields = ('user',)

class UserSerializer(serializers.ModelSerializer):
    influencer_profile = InfluencerProfileSerializer(read_only=True)
    company_profile = CompanyProfileSerializer(read_only=True)
    
    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'user_type', 'phone', 'is_verified', 
                 'created_at', 'influencer_profile', 'company_profile')
        read_only_fields = ('id', 'created_at')


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, min_length=8)
    
    def validate_new_password(self, value):
        """
        Validate new password strength
        """
        if len(value) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters long.")
        
        if not any(char.islower() for char in value):
            raise serializers.ValidationError("Password must contain at least one lowercase letter.")
        
        if not any(char.isupper() for char in value):
            raise serializers.ValidationError("Password must contain at least one uppercase letter.")
        
        if not any(char.isdigit() for char in value):
            raise serializers.ValidationError("Password must contain at least one number.")
        
        return value