from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.db import IntegrityError
from django.utils import timezone

from rest_framework import generics, status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from core.models import EmailVerification
from .serializers import CustomRegisterSerializer, EmailVerificationSerializer


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
            verification = EmailVerification.objects.get(
                verification_pin=verification_pin,
                user__email=email,
                is_verified=False,
            )
            if verification.expires_at <= timezone.now():
                raise ValidationError("Verification pin has expired.")
            verification.is_verified = True
            verification.save()
            verification.user.is_active = True
            verification.user.save()
            return Response(
                {'status': 'email verified'},
                status=status.HTTP_200_OK)
        except EmailVerification.DoesNotExist:
            raise ValidationError("Invalid verification pin.")
