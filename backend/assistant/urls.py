from django.urls import path
from .views import AskAssistantView, AssistantStatusView

urlpatterns = [
    path('ask/', AskAssistantView.as_view(), name='ask-assistant'),
    path('status/', AssistantStatusView.as_view(), name='assistant-status'),
]
