from django.urls import path
from . import views

urlpatterns = [
    path('threads/', views.ThreadListCreateView.as_view(), name='thread-list-create'),
    path('threads/<int:pk>/', views.ThreadDetailView.as_view(), name='thread-detail'),
    path('threads/<int:thread_id>/sessions/', views.ChatSessionListCreateView.as_view(), name='chat-session-list-create'),
    path('sessions/<int:pk>/', views.ChatSessionDetailView.as_view(), name='chat-session-detail'),
    path('sessions/<int:session_id>/messages/', views.ChatMessageListCreateView.as_view(), name='chat-message-list-create'),
]
