from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q

from apps.users.models import CustomUser, Profile
from apps.users.serializers import UserSerializer, UserCreateSerializer
from apps.posts.models import Post, Comment, Like
from apps.posts.serializers import PostSerializer, CommentSerializer, LikeSerializer
from apps.social.models import Follow, Notification
from apps.social.serializers import FollowSerializer, NotificationSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['username', 'email', 'bio']
    ordering_fields = ['date_joined', 'username']

    def get_permissions(self):
        if self.action == 'create':
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        return UserSerializer

    @action(detail=False, methods=['get'])
    def me(self, request):
        """Obtenir les informations de l'utilisateur connecté"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def posts(self, request, pk=None):
        """Obtenir les posts d'un utilisateur"""
        user = self.get_object()
        posts = Post.objects.filter(author=user)
        serializer = PostSerializer(posts, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def followers(self, request, pk=None):
        """Obtenir les abonnés d'un utilisateur"""
        user = self.get_object()
        followers = Follow.objects.filter(following=user)
        serializer = FollowSerializer(followers, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def following(self, request, pk=None):
        """Obtenir les abonnements d'un utilisateur"""
        user = self.get_object()
        following = Follow.objects.filter(follower=user)
        serializer = FollowSerializer(following, many=True)
        return Response(serializer.data)


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['post_type', 'author']
    search_fields = ['content']
    ordering_fields = ['created_at', 'likes_count', 'comments_count']
    ordering = ['-created_at']

    def perform_create(self, serializer):
        post = serializer.save(author=self.request.user)

        # Déterminer le type de post
        if self.request.FILES.get('image'):
            post.post_type = 'image'
        elif self.request.FILES.get('video'):
            post.post_type = 'video'
        else:
            post.post_type = 'text'
        post.save()

        # Mettre à jour le compteur
        self.request.user.profile.posts_count += 1
        self.request.user.profile.save()

    @action(detail=False, methods=['get'])
    def feed(self, request):
        """Obtenir le fil d'actualités de l'utilisateur"""
        following_users = Follow.objects.filter(
            follower=request.user
        ).values_list('following', flat=True)

        posts = Post.objects.filter(
            Q(author__in=following_users) | Q(author=request.user)
        ).select_related('author', 'author__profile')

        page = self.paginate_queryset(posts)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(posts, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def like(self, request, pk=None):
        """Liker/unliker un post"""
        post = self.get_object()
        like, created = Like.objects.get_or_create(
            user=request.user,
            content_type='post',
            post=post
        )

        if not created:
            like.delete()
            post.likes_count -= 1
            liked = False
        else:
            post.likes_count += 1
            liked = True

            # Créer une notification
            if post.author != request.user:
                Notification.objects.create(
                    recipient=post.author,
                    sender=request.user,
                    notification_type='like',
                    post=post,
                    message=f"{request.user.username} a aimé votre post"
                )

        post.save()

        return Response({
            'liked': liked,
            'likes_count': post.likes_count
        })

    @action(detail=True, methods=['get'])
    def comments(self, request, pk=None):
        """Obtenir les commentaires d'un post"""
        post = self.get_object()
        comments = Comment.objects.filter(post=post, parent=None)
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['post']
    ordering = ['-created_at']

    def perform_create(self, serializer):
        comment = serializer.save(author=self.request.user)

        # Mettre à jour le compteur
        comment.post.comments_count += 1
        comment.post.save()

        # Créer une notification
        if comment.post.author != self.request.user:
            Notification.objects.create(
                recipient=comment.post.author,
                sender=self.request.user,
                notification_type='comment',
                post=comment.post,
                comment=comment,
                message=f"{self.request.user.username} a commenté votre post"
            )

    @action(detail=True, methods=['post'])
    def like(self, request, pk=None):
        """Liker/unliker un commentaire"""
        comment = self.get_object()
        like, created = Like.objects.get_or_create(
            user=request.user,
            content_type='comment',
            comment=comment
        )

        if not created:
            like.delete()
            comment.likes_count -= 1
            liked = False
        else:
            comment.likes_count += 1
            liked = True

        comment.save()

        return Response({
            'liked': liked,
            'likes_count': comment.likes_count
        })


class FollowViewSet(viewsets.ModelViewSet):
    queryset = Follow.objects.all()
    serializer_class = FollowSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['post'])
    def toggle(self, request):
        """Suivre/ne plus suivre un utilisateur"""
        following_id = request.data.get('following_id')

        if not following_id:
            return Response(
                {'error': 'following_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user_to_follow = CustomUser.objects.get(id=following_id)
        except CustomUser.DoesNotExist:
            return Response(
                {'error': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        if user_to_follow == request.user:
            return Response(
                {'error': 'Cannot follow yourself'},
                status=status.HTTP_400_BAD_REQUEST
            )

        follow, created = Follow.objects.get_or_create(
            follower=request.user,
            following=user_to_follow
        )

        if not created:
            follow.delete()
            request.user.profile.following_count -= 1
            user_to_follow.profile.followers_count -= 1
            following = False
        else:
            request.user.profile.following_count += 1
            user_to_follow.profile.followers_count += 1
            following = True

            # Créer une notification
            Notification.objects.create(
                recipient=user_to_follow,
                sender=request.user,
                notification_type='follow',
                message=f"{request.user.username} vous suit maintenant"
            )

        request.user.profile.save()
        user_to_follow.profile.save()

        return Response({
            'following': following,
            'followers_count': user_to_follow.profile.followers_count
        })


class NotificationViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user)

    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        """Obtenir le nombre de notifications non lues"""
        count = self.get_queryset().filter(is_read=False).count()
        return Response({'unread_count': count})

    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        """Marquer toutes les notifications comme lues"""
        self.get_queryset().update(is_read=True)
        return Response({'message': 'All notifications marked as read'})

    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """Marquer une notification comme lue"""
        notification = self.get_object()
        notification.is_read = True
        notification.save()
        return Response({'message': 'Notification marked as read'})
