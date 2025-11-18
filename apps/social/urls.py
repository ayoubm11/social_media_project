from django.urls import path
from . import views

app_name = 'social'

urlpatterns = [
    path('follow/<str:username>/', views.follow_user, name='follow_user'),
    path('chat/<str:username>/', views.start_chat, name='start_chat'),
    path('notifications/', views.notifications, name='notifications'),
    path('notifications/<int:pk>/read/', views.mark_notification_read, name='mark_notification_read'),

    path('followers/<str:username>/', views.followers_list, name='followers_list'),
    path('following/<str:username>/', views.following_list, name='following_list'),
    path('suggestions/', views.suggestions, name='suggestions'),
    path('search/', views.search_users, name='search_users'),
]