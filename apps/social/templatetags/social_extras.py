from django import template
from django.db.models import Count
from apps.users.models import CustomUser
from apps.social.models import Follow

register = template.Library()


@register.simple_tag
def get_suggestions(user, limit=5):
    """Obtenir des suggestions d'utilisateurs à suivre"""
    if not user.is_authenticated:
        return []

    # Récupérer les utilisateurs déjà suivis
    following_ids = Follow.objects.filter(
        follower=user
    ).values_list('following_id', flat=True)

    # Suggestions basées sur les utilisateurs populaires
    suggestions = CustomUser.objects.exclude(
        id__in=following_ids
    ).exclude(
        id=user.id
    ).annotate(
        followers_count_real=Count('followers')
    ).order_by('-followers_count_real')[:limit]

    return suggestions


@register.filter
def is_following(user, target_user):
    """Vérifier si user suit target_user"""
    if not user.is_authenticated:
        return False

    return Follow.objects.filter(
        follower=user,
        following=target_user
    ).exists()


@register.filter
def has_liked_post(user, post):
    """Vérifier si user a liké le post"""
    if not user.is_authenticated:
        return False

    from apps.posts.models import Like
    return Like.objects.filter(
        user=user,
        content_type='post',
        post=post
    ).exists()


@register.filter
def has_liked_comment(user, comment):
    """Vérifier si user a liké le commentaire"""
    if not user.is_authenticated:
        return False

    from apps.posts.models import Like
    return Like.objects.filter(
        user=user,
        content_type='comment',
        comment=comment
    ).exists()


@register.simple_tag
def get_mutual_friends_count(user, target_user):
    """Obtenir le nombre d'amis communs"""
    if not user.is_authenticated:
        return 0

    user_following = set(Follow.objects.filter(
        follower=user
    ).values_list('following_id', flat=True))

    target_following = set(Follow.objects.filter(
        follower=target_user
    ).values_list('following_id', flat=True))

    return len(user_following.intersection(target_following))