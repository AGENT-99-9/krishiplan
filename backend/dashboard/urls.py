from django.urls import path
from .views import DashboardStatsView, RecentActivityView, UserProfileView
from .admin_views import AdminStatsView, AdminUsersView, AdminProductsView, AdminPostsView

urlpatterns = [
    path('stats/', DashboardStatsView.as_view(), name='dashboard-stats'),
    path('activity/', RecentActivityView.as_view(), name='recent-activity'),
    path('profile/', UserProfileView.as_view(), name='profile'),
    
    # Admin Portal Routes
    path('admin/stats/', AdminStatsView.as_view(), name='admin-stats'),
    path('admin/users/', AdminUsersView.as_view(), name='admin-users'),
    path('admin/users/<str:pk>/', AdminUsersView.as_view(), name='admin-users-detail'),
    path('admin/products/', AdminProductsView.as_view(), name='admin-products'),
    path('admin/products/<str:pk>/', AdminProductsView.as_view(), name='admin-products-detail'),
    path('admin/posts/', AdminPostsView.as_view(), name='admin-posts'),
    path('admin/posts/<str:pk>/', AdminPostsView.as_view(), name='admin-posts-detail'),
]
