from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Q, Count, Max
from apps.users.models import CustomUser
from .models import Follow, Notification, Conversation, Message


@login_required
def follow_user(request, username):
    """Suivre/ne plus suivre un utilisateur"""
    if request.method == 'POST':
        user_to_follow = get_object_or_404(CustomUser, username=username)

        if user_to_follow == request.user:
            return JsonResponse({'error': 'Cannot follow yourself'}, status=400)

        follow, created = Follow.objects.get_or_create(
            follower=request.user,
            following=user_to_follow
        )

        if not created:
            # Unfollow
            follow.delete()
            request.user.profile.following_count -= 1
            user_to_follow.profile.followers_count -= 1
            following = False
        else:
            # Follow
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

        return JsonResponse({
            'following': following,
            'followers_count': user_to_follow.profile.followers_count
        })

    return JsonResponse({'error': 'Method not allowed'}, status=405)


@login_required
def notifications(request):
    """Liste des notifications"""
    notifications = request.user.notifications.all()[:20]
    unread_count = request.user.notifications.filter(is_read=False).count()

    context = {
        'notifications': notifications,
        'unread_count': unread_count
    }
    return render(request, 'social/notifications.html', context)


@login_required
def mark_notification_read(request, pk):
    """Marquer une notification comme lue"""
    notification = get_object_or_404(Notification, pk=pk, recipient=request.user)
    notification.is_read = True
    notification.save()
    return JsonResponse({'success': True})


@login_required
def followers_list(request, username):
    """Liste des abonnés d'un utilisateur"""
    user = get_object_or_404(CustomUser, username=username)
    followers = Follow.objects.filter(following=user).select_related('follower', 'follower__profile')

    # Vérifier quels followers l'utilisateur connecté suit
    if request.user.is_authenticated:
        user_following_ids = Follow.objects.filter(
            follower=request.user
        ).values_list('following_id', flat=True)
    else:
        user_following_ids = []

    context = {
        'profile_user': user,
        'followers': followers,
        'user_following_ids': list(user_following_ids),
        'tab': 'followers'
    }
    return render(request, 'social/followers_list.html', context)


@login_required
def following_list(request, username):
    """Liste des abonnements d'un utilisateur"""
    user = get_object_or_404(CustomUser, username=username)
    following = Follow.objects.filter(follower=user).select_related('following', 'following__profile')

    # Vérifier quels utilisateurs l'utilisateur connecté suit
    if request.user.is_authenticated:
        user_following_ids = Follow.objects.filter(
            follower=request.user
        ).values_list('following_id', flat=True)
    else:
        user_following_ids = []

    context = {
        'profile_user': user,
        'following': following,
        'user_following_ids': list(user_following_ids),
        'tab': 'following'
    }
    return render(request, 'social/following_list.html', context)


@login_required
def suggestions(request):
    """Suggestions d'utilisateurs à suivre"""
    # Récupérer les utilisateurs que l'on suit déjà
    following_ids = Follow.objects.filter(
        follower=request.user
    ).values_list('following_id', flat=True)

    # Récupérer les suggestions basées sur :
    # 1. Les utilisateurs suivis par les personnes qu'on suit
    # 2. Les utilisateurs populaires (avec le plus de followers)
    # 3. Les nouveaux utilisateurs

    # Suggestions des amis d'amis
    friends_of_friends = CustomUser.objects.filter(
        followers__follower_id__in=following_ids
    ).exclude(
        id__in=following_ids
    ).exclude(
        id=request.user.id
    ).annotate(
        mutual_friends=Count('followers')
    ).order_by('-mutual_friends')[:5]

    # Utilisateurs populaires
    popular_users = CustomUser.objects.exclude(
        id__in=following_ids
    ).exclude(
        id=request.user.id
    ).annotate(
        followers_count_real=Count('followers')
    ).order_by('-followers_count_real')[:5]

    # Nouveaux utilisateurs
    new_users = CustomUser.objects.exclude(
        id__in=following_ids
    ).exclude(
        id=request.user.id
    ).order_by('-date_joined')[:5]

    # Combiner et dédupliquer
    suggestions_set = set()
    suggestions_list = []

    for user in list(friends_of_friends) + list(popular_users) + list(new_users):
        if user.id not in suggestions_set and len(suggestions_list) < 10:
            suggestions_set.add(user.id)
            suggestions_list.append(user)

    context = {
        'suggestions': suggestions_list,
    }
    return render(request, 'social/suggestions.html', context)


@login_required
def search_users(request):
    """Recherche d'utilisateurs"""
    query = request.GET.get('q', '')

    if query:
        users = CustomUser.objects.filter(
            Q(username__icontains=query) |
            Q(email__icontains=query) |
            Q(bio__icontains=query)
        ).exclude(id=request.user.id).select_related('profile')[:20]
    else:
        users = CustomUser.objects.none()

    # Vérifier quels utilisateurs l'utilisateur connecté suit
    user_following_ids = Follow.objects.filter(
        follower=request.user
    ).values_list('following_id', flat=True)

    context = {
        'users': users,
        'query': query,
        'user_following_ids': list(user_following_ids),
    }
    return render(request, 'social/search_users.html', context)


@login_required
def list_conversations(request):
    """Liste toutes les conversations de l'utilisateur connecté"""
    # Récupérer toutes les conversations où l'utilisateur est participant
    # Filtrer uniquement les conversations avec exactement 2 participants
    conversations = Conversation.objects.filter(participants=request.user).annotate(
        participant_count=Count('participants'),
        last_message_time=Max('messages__created_at')
    ).filter(participant_count=2).prefetch_related('participants', 'participants__profile', 'messages__sender')
    
    # Préparer les données pour chaque conversation
    conversations_list = []
    for conv in conversations:
        # Trouver l'autre participant (celui qui n'est pas l'utilisateur connecté)
        other_participant = None
        for participant in conv.participants.all():
            if participant.id != request.user.id:
                other_participant = participant
                break
        
        # Si pas d'autre participant, passer à la suivante
        if not other_participant:
            continue
        
        # Récupérer le dernier message
        last_message = conv.messages.order_by('-created_at').first()
        
        # Compter les messages non lus (seulement ceux de l'autre participant)
        unread_count = conv.messages.filter(
            sender=other_participant,
            read_at__isnull=True
        ).count()
        
        # Déterminer si le dernier message est envoyé par l'utilisateur connecté
        is_sender = last_message and last_message.sender.id == request.user.id if last_message else False
        
        conversations_list.append({
            'conversation': conv,
            'other_participant': other_participant,
            'last_message': last_message,
            'is_sender': is_sender,
            'unread_count': unread_count,
        })
    
    # Trier par date du dernier message (ou date de création si pas de message)
    from django.utils import timezone
    def get_sort_date(item):
        conv = item['conversation']
        if hasattr(conv, 'last_message_time') and conv.last_message_time:
            return conv.last_message_time
        return getattr(conv, 'created_at', timezone.now())
    
    conversations_list.sort(key=get_sort_date, reverse=True)
    
    context = {
        'conversations_list': conversations_list,
    }
    return render(request, 'social/conversations_list.html', context)


@login_required
def start_chat(request, username):
    """Afficher la page de démarrage de chat avec un utilisateur cible."""
    user_to_chat = get_object_or_404(CustomUser, username=username)

    # Ne pas permettre de chatter avec soi-même — rediriger vers le profil
    if user_to_chat == request.user:
        return redirect('users:profile', username=request.user.username)

    # Trouver une conversation existante entre les deux utilisateurs (avec filtrage direct)
    conversations = Conversation.objects.filter(participants=request.user).filter(participants=user_to_chat)
    # Filtrer celles avec exactement 2 participants
    conversation = None
    for conv in conversations:
        if conv.participants.count() == 2:
            conversation = conv
            break
    
    if not conversation:
        conversation = Conversation.objects.create()
        conversation.participants.add(request.user, user_to_chat)

    # Récupérer les messages existants
    msgs = Message.objects.filter(conversation=conversation).select_related('sender')
    messages = [
        {
            'id': m.id,
            'sender': m.sender.username,
            'content': m.content,
            'created_at': m.created_at.isoformat()
        }
        for m in msgs
    ]

    context = {
        'target_user': user_to_chat,
        'conversation': conversation,
        'messages': messages,
    }
    return render(request, 'social/start_chat.html', context)