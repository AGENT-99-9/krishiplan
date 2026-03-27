from django.urls import path
from .views import (
    PostListView, PostCreateView, TrendingTopicsView, 
    TopContributorsView, PostLikeView, PostCommentView, PingView
)

urlpatterns = [
    path('ping/', PingView.as_view(), name='community-ping'),
    path('posts/', PostListView.as_view(), name='post-list'),
    path('create/', PostCreateView.as_view(), name='post-create'),
    path('trending/', TrendingTopicsView.as_view(), name='trending-topics'),
    path('contributors/', TopContributorsView.as_view(), name='top-contributors'),
    path('posts/<str:post_id>/like/', PostLikeView.as_view(), name='post-like'),
    path('posts/<str:post_id>/comment/', PostCommentView.as_view(), name='post-comment'),
]
