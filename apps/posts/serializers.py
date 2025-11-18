from rest_framework import serializers
from .models import Post, Comment, Like
from apps.users.serializers import UserSerializer


class CommentSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    replies = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id', 'post', 'author', 'content', 'parent', 'likes_count',
                  'created_at', 'updated_at', 'replies']
        read_only_fields = ['author', 'created_at', 'updated_at']

    def get_replies(self, obj):
        if obj.replies.exists():
            return CommentSerializer(obj.replies.all(), many=True).data
        return []


class PostSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    is_liked = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ['id', 'author', 'content', 'post_type', 'image', 'video',
                  'likes_count', 'comments_count', 'shares_count',
                  'created_at', 'updated_at', 'comments', 'is_liked']
        read_only_fields = ['author', 'post_type', 'created_at', 'updated_at']

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Like.objects.filter(
                user=request.user,
                content_type='post',
                post=obj
            ).exists()
        return False


class LikeSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Like
        fields = ['id', 'user', 'content_type', 'post', 'comment', 'created_at']
        read_only_fields = ['user', 'created_at']

