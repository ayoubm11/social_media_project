from django.db import models
from apps.users.models import CustomUser


class Post(models.Model):
    POST_TYPES = (
        ('text', 'Text'),
        ('image', 'Image'),
        ('video', 'Video'),
    )

    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='posts')
    content = models.TextField(max_length=2000)
    post_type = models.CharField(max_length=10, choices=POST_TYPES, default='text')
    image = models.ImageField(upload_to='posts/images/', blank=True, null=True)
    video = models.FileField(upload_to='posts/videos/', blank=True, null=True)
    likes_count = models.IntegerField(default=0)
    comments_count = models.IntegerField(default=0)
    shares_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.author.username}'s post - {self.created_at.strftime('%Y-%m-%d')}"


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField(max_length=500)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    likes_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Comment by {self.author.username} on {self.post}"


class Like(models.Model):
    LIKE_TYPES = (
        ('post', 'Post'),
        ('comment', 'Comment'),
    )

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='likes')
    content_type = models.CharField(max_length=10, choices=LIKE_TYPES)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True, blank=True, related_name='post_likes')
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, null=True, blank=True, related_name='comment_likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'content_type', 'post', 'comment')

    def __str__(self):
        return f"{self.user.username} likes {self.content_type}"