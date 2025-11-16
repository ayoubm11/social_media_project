from django.urls import path
from . import views

app_name = 'posts'

urlpatterns = [
    path('', views.feed, name='feed'),
    path('post/create/', views.create_post, name='create_post'),
    path('post/<int:pk>/', views.post_detail, name='post_detail'),
    path('post/<int:pk>/like/', views.like_post, name='like_post'),
    path('post/<int:pk>/delete/', views.delete_post, name='delete_post'),
    path('post/comment/<int:pk>/like/', views.like_comment, name='like_comment'),
    path('post/comment/<int:pk>/delete/', views.delete_comment, name='delete_comment'),
]