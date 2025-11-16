from rest_framework import serializers
from .models import CustomUser, Profile


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['profile_picture', 'cover_photo', 'followers_count',
                  'following_count', 'posts_count', 'created_at']


class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(read_only=True)

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'bio', 'location',
                  'website', 'birth_date', 'profile', 'date_joined']
        read_only_fields = ['date_joined']


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password']

    def create(self, validated_data):
        user = CustomUser.objects.create_user(**validated_data)
        return user