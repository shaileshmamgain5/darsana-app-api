from django.urls import path
from . import views

urlpatterns = [
    path('threads/', views.ThreadListView.as_view(), name='thread-list'),
    path('threads/<int:pk>/', views.ThreadDetailView.as_view(), name='thread-detail'),
    path('threads/<int:pk>/delete/', views.DeleteThreadView.as_view(), name='thread-delete'),
    path('sessions/<int:session_id>/end/', views.EndSessionView.as_view(), name='session-end'),
    path('response/', views.GetResponseView.as_view(), name='get-response'),
    path('response/<int:message_id>/cancel/', views.CancelResponseView.as_view(), name='cancel-response'),
]
