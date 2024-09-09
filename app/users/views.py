from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.db import IntegrityError
from django.utils import timezone

from rest_framework import generics, status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.contrib.auth import authenticate, login
from .utils import send_verification_email

from core.models import EmailVerification
from .serializers import (
    CustomRegisterSerializer,
    EmailVerificationSerializer,
    LoginSerializer,
    ForgotPasswordSerializer,
    ResetPasswordSerializer,
    ResendVerificationSerializer
)

from rest_framework.authtoken.models import Token


class RegisterView(generics.CreateAPIView):
    queryset = get_user_model().objects.all()
    serializer_class = CustomRegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        print(f"Request data: {request.data}")
        if serializer.is_valid():
            print("Serializer is valid")
        else:
            print(f"Serializer errors: {serializer.errors}")
        serializer.is_valid(raise_exception=True)
        try:
            user = serializer.save(request)
            print(f"User created: {user.email}")
            verification, created = EmailVerification.objects.get_or_create(user=user) # noqa
            print(f"Verification object: {verification}, Created: {created}")
            send_mail(
                'Verify your email',
                f'Your verification pin is {verification.verification_pin}',
                'from@example.com',
                [user.email],
                fail_silently=False,
            )
            print("Email sent successfully")
            headers = self.get_success_headers(serializer.data)
            return Response(
                {"detail": "Verification e-mail sent."},
                status=status.HTTP_201_CREATED, headers=headers)
        except IntegrityError as e:
            print(f"IntegrityError: {str(e)}")
            return Response(
                {"detail": "A user with this email already exists."},
                status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            return Response(
                {"detail": "An unexpected error occurred."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class VerifyEmailView(generics.CreateAPIView):
    serializer_class = EmailVerificationSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        verification_pin = request.data.get('verification_pin')
        email = request.data.get('email')

        if not email or not verification_pin:
            raise ValidationError(
                "Both email and verification pin are required."
            )

        try:
            user = get_user_model().objects.get(email=email)
            if user.is_active:
                return Response(
                    {'detail': 'Email is already verified.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            verification = EmailVerification.objects.get(
                verification_pin=verification_pin,
                user=user,
                is_verified=False,
            )
            if verification.expires_at <= timezone.now():
                raise ValidationError("Verification pin has expired.")
            verification.is_verified = True
            verification.save()
            user.is_active = True
            user.save()
            return Response(
                {'detail': 'Email verified successfully.'},
                status=status.HTTP_200_OK
            )
        except get_user_model().DoesNotExist:
            raise ValidationError("User with this email does not exist.")
        except EmailVerification.DoesNotExist:
            raise ValidationError("Invalid verification pin.")


class LoginView(generics.CreateAPIView):
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        if user.is_active:
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                "detail": "Login successful.",
                "token": token.key
            }, status=status.HTTP_200_OK)
        else:
            verification, created = EmailVerification.objects.get_or_create(user=user)
            if not created:
                verification.generate_new_pin()
            send_verification_email(user, verification.verification_pin)
            return Response(
                {"detail": "Email not verified. A new verification email has been sent."},
                status=status.HTTP_403_FORBIDDEN
            )


class ForgotPasswordView(generics.CreateAPIView):
    serializer_class = ForgotPasswordSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        user = get_user_model().objects.get(email=email)
        
        verification, created = EmailVerification.objects.get_or_create(user=user)
        if not created:
            verification.generate_new_pin()
        
        send_verification_email(user, verification.verification_pin)
        
        return Response(
            {"detail": "Password reset email sent."},
            status=status.HTTP_200_OK
        )


class ResetPasswordView(generics.CreateAPIView):
    serializer_class = ResetPasswordSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = get_user_model().objects.get(email=serializer.validated_data['email'])
        verification = EmailVerification.objects.get(
            user=user,
            verification_pin=serializer.validated_data['verification_pin']
        )
        
        try:
            password = serializer.validated_data['new_password']
            user.set_password(password)
            user.save()
            
            verification.is_verified = True
            verification.save()
            
            return Response(
                {"detail": "Password has been reset successfully."},
                status=status.HTTP_200_OK
            )
        except ValidationError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class ResendVerificationView(generics.CreateAPIView):
    serializer_class = ResendVerificationSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        user = get_user_model().objects.get(email=email)
        
        verification, created = EmailVerification.objects.get_or_create(user=user)
        if not created:
            verification.generate_new_pin()
        
        send_verification_email(user, verification.verification_pin)
        
        return Response(
            {"detail": "Verification email has been resent."},
            status=status.HTTP_200_OK
        )
