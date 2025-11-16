from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Q
from django.core.paginator import Paginator
from .models import Post, Comment, Like
from apps.social.models import Follow, Notification
from .forms import PostForm, CommentForm


@login_required
def feed(request):
    """Fil d'actualités avec les posts des utilisateurs suivis"""
    following_users = Follow.objects.filter(follower=request.user).values_list('following', flat=True)
    posts = Post.objects.filter(
        Q(author__in=following_users) | Q(author=request.user)
    ).select_related('author', 'author__profile').prefetch_related('comments', 'post_likes')

    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'posts': page_obj,
        'form': PostForm()
    }
    return render(request, 'posts/feed.html', context)


@login_required
def create_post(request):
    """Créer un nouveau post"""
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user

            # Déterminer le type de post
            if request.FILES.get('image'):
                post.post_type = 'image'
            elif request.FILES.get('video'):
                post.post_type = 'video'
            else:
                post.post_type = 'text'

            post.save()

            # Mettre à jour le compteur de posts
            request.user.profile.posts_count += 1
            request.user.profile.save()

            return redirect('posts:feed')
    else:
        form = PostForm()

    return render(request, 'posts/create_post.html', {'form': form})


@login_required
def post_detail(request, pk):
    """Détails d'un post avec commentaires"""
    post = get_object_or_404(Post, pk=pk)

    # Récupérer uniquement les commentaires de premier niveau (sans parent)
    comments = post.comments.filter(parent=None).select_related(
        'author',
        'author__profile'
    ).prefetch_related('replies', 'replies__author', 'replies__author__profile').order_by('-created_at')

    # Pagination des commentaires
    paginator = Paginator(comments, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Vérifier si l'utilisateur a liké le post
    user_liked_post = Like.objects.filter(
        user=request.user,
        content_type='post',
        post=post
    ).exists()

    # Récupérer les IDs des commentaires likés par l'utilisateur
    user_liked_comments = Like.objects.filter(
        user=request.user,
        content_type='comment',
        comment__post=post
    ).values_list('comment_id', flat=True)

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user

            # Gérer les réponses aux commentaires
            parent_id = request.POST.get('parent_id')
            if parent_id:
                parent_comment = get_object_or_404(Comment, id=parent_id)
                comment.parent = parent_comment

            comment.save()

            # Mettre à jour le compteur
            post.comments_count = post.comments.count()
            post.save()

            # Créer une notification
            if post.author != request.user:
                Notification.objects.create(
                    recipient=post.author,
                    sender=request.user,
                    notification_type='comment',
                    post=post,
                    comment=comment,
                    message=f"{request.user.username} a commenté votre post"
                )

            # Notification pour réponse à un commentaire
            if parent_id and parent_comment.author != request.user:
                Notification.objects.create(
                    recipient=parent_comment.author,
                    sender=request.user,
                    notification_type='comment',
                    post=post,
                    comment=comment,
                    message=f"{request.user.username} a répondu à votre commentaire"
                )

            return redirect('posts:post_detail', pk=pk)
    else:
        form = CommentForm()

    context = {
        'post': post,
        'comments': page_obj,
        'form': form,
        'user_liked_post': user_liked_post,
        'user_liked_comments': list(user_liked_comments),
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def like_post(request, pk):
    """Liker/unliker un post"""
    if request.method == 'POST':
        post = get_object_or_404(Post, pk=pk)
        like, created = Like.objects.get_or_create(
            user=request.user,
            content_type='post',
            post=post
        )

        if not created:
            # Unlike
            like.delete()
            post.likes_count -= 1
            liked = False
        else:
            # Like
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

        return JsonResponse({
            'liked': liked,
            'likes_count': post.likes_count
        })

    return JsonResponse({'error': 'Method not allowed'}, status=405)


@login_required
def like_comment(request, pk):
    """Liker/unliker un commentaire"""
    if request.method == 'POST':
        comment = get_object_or_404(Comment, pk=pk)
        like, created = Like.objects.get_or_create(
            user=request.user,
            content_type='comment',
            comment=comment
        )

        if not created:
            # Unlike
            like.delete()
            comment.likes_count -= 1
            liked = False
        else:
            # Like
            comment.likes_count += 1
            liked = True

            # Créer une notification
            if comment.author != request.user:
                Notification.objects.create(
                    recipient=comment.author,
                    sender=request.user,
                    notification_type='like',
                    comment=comment,
                    post=comment.post,
                    message=f"{request.user.username} a aimé votre commentaire"
                )

        comment.save()

        return JsonResponse({
            'liked': liked,
            'likes_count': comment.likes_count
        })

    return JsonResponse({'error': 'Method not allowed'}, status=405)


@login_required
def delete_post(request, pk):
    """Supprimer un post"""
    post = get_object_or_404(Post, pk=pk, author=request.user)
    if request.method == 'POST':
        request.user.profile.posts_count -= 1
        request.user.profile.save()
        post.delete()
        return redirect('posts:feed')
    return render(request, 'posts/delete_confirm.html', {'post': post})


@login_required
def delete_comment(request, pk):
    """Supprimer un commentaire"""
    comment = get_object_or_404(Comment, pk=pk, author=request.user)
    post_id = comment.post.id

    if request.method == 'POST':
        # Mettre à jour le compteur
        post = comment.post
        post.comments_count = post.comments.count() - 1
        post.save()

        comment.delete()
        return redirect('posts:post_detail', pk=post_id)

    return render(request, 'posts/delete_comment_confirm.html', {'comment': comment})