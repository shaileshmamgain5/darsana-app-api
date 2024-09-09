from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from unittest.mock import patch
from core.models import EmailVerification
from django.utils import timezone
from datetime import timedelta

REGISTER_URL = reverse('register')
VERIFY_EMAIL_URL = reverse('verify-email')
RESEND_VERIFICATION_URL = reverse('resend-verification')
LOGIN_URL = reverse('login')
FORGOT_PASSWORD_URL = reverse('forgot-password')
RESET_PASSWORD_URL = reverse('reset-password')


class UserApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    # User Registration Tests
    def test_create_user_success(self):
        # Test creating a new user successfully
        payload = {
            'email': 'test@example.com',
            'password': 'testpass123',
        }
        with patch('users.views.send_mail') as mock_send_mail:
            res = self.client.post(REGISTER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertIn('detail', res.data)
        self.assertEqual(res.data['detail'], 'Verification e-mail sent.')
        user = get_user_model().objects.get(email=payload['email'])
        self.assertTrue(user.check_password(payload['password']))
        self.assertFalse(user.is_active)
        mock_send_mail.assert_called_once()

    def test_user_with_email_exists_error(self):
        # Test creating a user that already exists fails
        payload = {'email': 'test@example.com', 'password': 'testpass123'}
        get_user_model().objects.create_user(**payload)
        res = self.client.post(REGISTER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short_error(self):
        # Test that the password must be more than 8 characters
        payload = {'email': 'test@example.com', 'password': 'pw'}
        res = self.client.post(REGISTER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        self.assertFalse(user_exists)

    def test_create_user_invalid_email(self):
        payload = {
            'email': 'notanemail',
            'password': 'testpass123',
        }
        res = self.client.post(REGISTER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_user_common_password(self):
        payload = {
            'email': 'test@example.com',
            'password': 'password',
        }
        res = self.client.post(REGISTER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_user_twice(self):
        payload = {
            'email': 'test@example.com',
            'password': 'testpass123',
        }
        self.client.post(REGISTER_URL, payload)
        res = self.client.post(REGISTER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    @patch('users.views.send_mail')
    def test_verification_email_sent(self, mock_send_mail):
        payload = {
            'email': 'test@example.com',
            'password': 'testpass123',
        }
        res = self.client.post(REGISTER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        mock_send_mail.assert_called_once()
        self.assertIn(
            'Your verification pin is',
            mock_send_mail.call_args[0][1]
        )

    # Email Verification Tests
    @patch('users.views.EmailVerification.objects.get')
    def test_verify_email_success(self, mock_get):
        user = get_user_model().objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        user.is_active = False
        user.save()
        verification = EmailVerification.objects.create(user=user)
        mock_get.return_value = verification

        payload = {
            'email': 'test@example.com',
            'verification_pin': verification.verification_pin
        }
        res = self.client.post(VERIFY_EMAIL_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['detail'], 'Email verified successfully.')
        user.refresh_from_db()
        self.assertTrue(user.is_active)
        verification.refresh_from_db()
        self.assertTrue(verification.is_verified)

    def test_verify_email_invalid_pin(self):
        # Test email verification with invalid pin
        payload = {
            'email': 'test@example.com',
            'password': 'testpass123',
        }
        self.client.post(REGISTER_URL, payload)
        user = get_user_model().objects.get(email=payload['email'])

        verification_payload = {
            'email': 'test@example.com',
            'verification_pin': '000000'
        }
        res = self.client.post(VERIFY_EMAIL_URL, verification_payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user.refresh_from_db()
        self.assertFalse(user.is_active)

    def test_verify_email_expired_pin(self):
        # Test email verification with expired pin
        user = get_user_model().objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        user.is_active = False
        user.save()
        verification = EmailVerification.objects.create(user=user)
        verification.expires_at = timezone.now() - timedelta(days=1)
        verification.save()

        payload = {
            'email': 'test@example.com',
            'verification_pin': verification.verification_pin
        }
        res = self.client.post(VERIFY_EMAIL_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user.refresh_from_db()
        self.assertFalse(user.is_active)

    def test_verify_email_already_verified(self):
        # Test verifying an already verified email
        user = get_user_model().objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        user.is_active = True
        user.save()
        verification = EmailVerification.objects.create(user=user)

        payload = {
            'email': 'test@example.com',
            'verification_pin': verification.verification_pin
        }
        res = self.client.post(VERIFY_EMAIL_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(res.data['detail'], 'Email is already verified.')

    def test_verify_email_nonexistent_email(self):
        payload = {
            'email': 'nonexistent@example.com',
            'verification_pin': '123456'
        }
        res = self.client.post(VERIFY_EMAIL_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_verify_email_missing_fields(self):
        res1 = self.client.post(
            VERIFY_EMAIL_URL,
            {'email': 'test@example.com'}
        )
        self.assertEqual(res1.status_code, status.HTTP_400_BAD_REQUEST)

        res2 = self.client.post(
            VERIFY_EMAIL_URL,
            {'verification_pin': '123456'}
        )
        self.assertEqual(res2.status_code, status.HTTP_400_BAD_REQUEST)

    # Resend Verification Tests
    def test_resend_verification_email(self):
        user = get_user_model().objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        user.is_active = False
        user.save()

        payload = {'email': 'test@example.com'}
        with patch('users.views.send_verification_email') as mock_send:
            res = self.client.post(RESEND_VERIFICATION_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['detail'], 'Verification email has been resent.')
        mock_send.assert_called_once()

    def test_resend_verification_email_to_verified_user(self):
        user = get_user_model().objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        user.is_active = True
        user.save()

        payload = {'email': 'test@example.com'}
        res = self.client.post(RESEND_VERIFICATION_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_resend_verification_email_to_nonexistent_user(self):
        res = self.client.post(RESEND_VERIFICATION_URL, {'email': 'nonexistent@example.com'})
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    # Login Tests
    def test_login_success(self):
        # Test successful login
        user = get_user_model().objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        user.is_active = True
        user.save()
        payload = {
            'email': 'test@example.com',
            'password': 'testpass123'
        }
        res = self.client.post(LOGIN_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('token', res.data)

    def test_login_unverified_user(self):
        # Test login attempt with unverified user
        user = get_user_model().objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        user.is_active = False
        user.save()

        payload = {
            'email': 'test@example.com',
            'password': 'testpass123'
        }
        with patch('users.views.send_verification_email') as mock_send:
            res = self.client.post(LOGIN_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn('detail', res.data)
        self.assertEqual(res.data['detail'], 'Email not verified. A new verification email has been sent.')
        mock_send.assert_called_once()

    # Password Reset Tests
    def test_forgot_password(self):
        # Test forgot password functionality
        user = get_user_model().objects.create_user(
            email='test@example.com',
            password='testpass123'
        )

        payload = {'email': 'test@example.com'}
        with patch('users.views.send_verification_email') as mock_send:
            res = self.client.post(FORGOT_PASSWORD_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['detail'], 'Password reset email sent.')
        mock_send.assert_called_once()

    def test_reset_password(self):
        # Test reset password functionality
        user = get_user_model().objects.create_user(
            email='test@example.com',
            password='oldpassword123'
        )
        verification = EmailVerification.objects.create(user=user)

        payload = {
            'email': 'test@example.com',
            'verification_pin': verification.verification_pin,
            'new_password': 'newpassword123'
        }
        res = self.client.post(RESET_PASSWORD_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['detail'], 'Password has been reset successfully.')
        user.refresh_from_db()
        self.assertTrue(user.check_password('newpassword123'))
