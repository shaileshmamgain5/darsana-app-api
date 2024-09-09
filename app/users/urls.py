from django.urls import path
from .views import (
    RegisterView,
    VerifyEmailView,
    LoginView,
    ForgotPasswordView,
    ResetPasswordView,
    ResendVerificationView,
    UserDetailView,
    UserDeleteView
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('verify-email/', VerifyEmailView.as_view(), name='verify-email'),
    path('login/', LoginView.as_view(), name='login'),
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot-password'),
    path('reset-password/', ResetPasswordView.as_view(), name='reset-password'),
    path('resend-verification/', ResendVerificationView.as_view(), name='resend-verification'),
    path('me/', UserDetailView.as_view(), name='user-detail'),
    path('me/delete/', UserDeleteView.as_view(), name='user-delete'),
]
