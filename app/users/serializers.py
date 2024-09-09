from rest_framework import serializers
from django.contrib.auth import get_user_model
from core.models import EmailVerification
from dj_rest_auth.registration.serializers import RegisterSerializer
from allauth.account.adapter import get_adapter
from django.utils.translation import gettext as _
from django.contrib.auth import authenticate

def email_address_exists(email):
    User = get_user_model()
    exists = User.objects.filter(email__iexact=email).exists()
    print(f"Checking if email {email} exists: {exists}")
    return exists


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ['email', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = get_user_model().objects.create_user(**validated_data)
        EmailVerification.objects.create(user=user)
        return user


class EmailVerificationSerializer(serializers.Serializer):
    email = serializers.EmailField()
    verification_pin = serializers.CharField(max_length=6)


class CustomRegisterSerializer(RegisterSerializer):
    username = None
    password1 = None
    password2 = None
    password = serializers.CharField(write_only=True)

    class Meta:
        model = get_user_model()
        fields = ('email', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def validate_email(self, email):
        email = get_adapter().clean_email(email)
        if email and email_address_exists(email):
            raise serializers.ValidationError(
                _("A user is already registered with this e-mail address."))
        return email

    def validate_password(self, password):
        return get_adapter().clean_password(password)

    def get_cleaned_data(self):
        return {
            'password1': self.validated_data.get('password', ''),
            'email': self.validated_data.get('email', ''),
        }

    def validate(self, data):
        if 'password' not in data:
            raise serializers.ValidationError({
                "password": "This field is required."
            })

        # Add password1 and password2 to the data
        # for dj-rest-auth compatibility
        data['password1'] = data['password']
        data['password2'] = data['password']

        return super().validate(data)

    def save(self, request):
        adapter = get_adapter()
        user = adapter.new_user(request)
        self.cleaned_data = self.get_cleaned_data()
        user = adapter.save_user(request, user, self, commit=False)
        user.is_active = False  # Set user as inactive initially
        user.save()
        self.custom_signup(request, user)
        EmailVerification.objects.create(user=user)
        return user


class LoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()
    password = serializers.CharField(style={'input_type': 'password'}, write_only=True)

    class Meta:
        model = get_user_model()
        fields = ['email', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = get_user_model().objects.filter(email=email).first()
            if user and user.check_password(password):
                attrs['user'] = user
                return attrs
        raise serializers.ValidationError("Unable to log in with provided credentials.")
