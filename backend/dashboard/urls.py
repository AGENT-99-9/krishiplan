from django.urls import path
from .views import DashboardStatsView, RecentActivityView, UserProfileView

urlpatterns = [
    path('stats/', DashboardStatsView.as_view(), name='dashboard-stats'),
    path('activity/', RecentActivityView.as_view(), name='recent-activity'),
    path('profile/', UserProfileView.as_view(), name='profile'),
]
