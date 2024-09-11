from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone

from rest_framework import generics, status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import login
from core.utils import send_verification_email

from core.models import EmailVerification
from .serializers import (
    CustomRegisterSerializer,
    EmailVerificationSerializer,
    LoginSerializer,
    ForgotPasswordSerializer,
    ResetPasswordSerializer,
    ResendVerificationSerializer,
    UserSerializer
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
            with transaction.atomic():
                user = serializer.save(request)
                print(f"User created: {user.email}")
                verification, created = EmailVerification.objects.get_or_create(user=user) # noqa
                print(
                    f"Verification object: {verification}, Created: {created}"
                    )
                send_verification_email(user, verification.verification_pin)
        except ValidationError as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            print(f"An error occurred during registration: {e}")
            return Response(
                {"detail": "An error occurred during registration. Please try again."}, # noqa
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        headers = self.get_success_headers(serializer.data)
        return Response(
            {"detail": "Verification e-mail sent."},
            status=status.HTTP_201_CREATED,
            headers=headers
        )


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
            verification = EmailVerification.objects.get(
                verification_pin=verification_pin,
                user=user,
            )
            
            if user.is_active and verification.is_verified:
                return Response(
                    {'detail': 'Email is already verified and account is active.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if verification.expires_at <= timezone.now():
                raise ValidationError("Verification pin has expired.")
            
            verification.is_verified = True
            verification.save()
            user.is_active = True
            user.save()
            return Response(
                {'detail': 'Email verified successfully and account activated.'},
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
            login(
                request,
                user,
                backend='django.contrib.auth.backends.ModelBackend'
                )
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                "detail": "Login successful.",
                "token": token.key
            }, status=status.HTTP_200_OK)
        else:
            verification, created = EmailVerification.objects.get_or_create(user=user) # noqa
            if not created:
                verification.generate_new_pin()
            send_verification_email(user, verification.verification_pin)
            return Response(
                {"detail": "Email not verified. A new verification email has been sent."}, # noqa
                status=status.HTTP_403_FORBIDDEN
            )


class ForgotPasswordView(generics.CreateAPIView):
    serializer_class = ForgotPasswordSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']

        try:
            user = get_user_model().objects.get(email=email)
            verification, created = EmailVerification.objects.get_or_create(user=user)
            if not created:
                verification.generate_new_pin()
            send_verification_email(user, verification.verification_pin)
            return Response(
                {"detail": "Password reset email sent."},
                status=status.HTTP_200_OK
            )
        except get_user_model().DoesNotExist:
            return Response(
                {"detail": "User with this email does not exist."},
                status=status.HTTP_404_NOT_FOUND
            )


class ResetPasswordView(generics.CreateAPIView):
    serializer_class = ResetPasswordSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = get_user_model().objects.get(
            email=serializer.validated_data['email']
            )
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
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class ResendVerificationView(generics.CreateAPIView):
    serializer_class = ResendVerificationSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        user = get_user_model().objects.get(email=email)

        verification, created = EmailVerification.objects.get_or_create(user=user) # noqa
        if not created:
            verification.generate_new_pin()

        send_verification_email(user, verification.verification_pin)
        return Response(
            {"detail": "Verification email has been resent."},
            status=status.HTTP_200_OK
        )


class UserDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(
            instance,
            data=request.data,
            partial=partial
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

    def perform_update(self, serializer):
        serializer.save()
        if 'password' in self.request.data:
            instance = serializer.instance
            instance.set_password(self.request.data['password'])
            instance.save()


class UserDeleteView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def destroy(self, request, *args, **kwargs):
        user = self.get_object()
        # Delete all related data
        EmailVerification.objects.filter(user=user).delete()
        # Add any other related models that need to be deleted here

        # Delete the user
        user.delete()
        return Response({"detail": "User account and all associated data have been deleted."}, status=status.HTTP_200_OK) # noqa
