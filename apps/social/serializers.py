from rest_framework import serializers
from .models import Follow, Notification
from apps.users.serializers import UserSerializer


class FollowSerializer(serializers.ModelSerializer):
    follower = UserSerializer(read_only=True)
    following = UserSerializer(read_only=True)

    class Meta:
        model = Follow
        fields = ['id', 'follower', 'following', 'created_at']
        read_only_fields = ['follower', 'created_at']


class NotificationSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)

    class Meta:
        model = Notification
        fields = ['id', 'recipient', 'sender', 'notification_type',
                  'post', 'comment', 'message', 'is_read', 'created_at']
        read_only_fields = ['sender', 'created_at']