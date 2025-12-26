# for_authorization/tests.py
from django.test import TestCase, Client
from django.urls import reverse
from django.core import mail
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from .forms import (
    ViewerRegistrationForm,
    MusicianRegistrationForm,
    VenueOwnerRegistrationForm
)

User = get_user_model()

class UserModelTests(TestCase):
    def test_role_methods(self):
        viewer = User.objects.create_user(
            username='viewer',
            email='viewer@example.com',
            password='password123',
            role='viewer'
        )
        musician = User.objects.create_user(
            username='musician',
            email='musician@example.com',
            password='password123',
            role='musician'
        )
        manager = User.objects.create_user(
            username='manager',
            email='manager@example.com',
            password='password123',
            role='manager'
        )
        venue_owner = User.objects.create_user(
            username='venue_owner',
            email='venue@example.com',
            password='password123',
            role='venue_owner'
        )
        
        self.assertTrue(viewer.is_viewer())
        self.assertFalse(viewer.is_musician())
        self.assertFalse(viewer.is_manager())
        self.assertFalse(viewer.is_venue_owner())
        
        self.assertTrue(musician.is_musician())
        self.assertFalse(musician.is_viewer())
        self.assertFalse(musician.is_manager())
        self.assertFalse(musician.is_venue_owner())
        
        self.assertTrue(manager.is_manager())
        self.assertFalse(manager.is_viewer())
        self.assertFalse(manager.is_musician())
        self.assertFalse(manager.is_venue_owner())
        
        self.assertTrue(venue_owner.is_venue_owner())
        self.assertFalse(venue_owner.is_viewer())
        self.assertFalse(venue_owner.is_musician())
        self.assertFalse(venue_owner.is_manager())
        
        self.assertTrue(manager.can_manage_bands())
        self.assertTrue(venue_owner.can_manage_bands())
        self.assertFalse(musician.can_manage_bands())
        self.assertFalse(viewer.can_manage_bands())
        
        self.assertFalse(viewer.can_book_rehearsals())
        self.assertTrue(musician.can_book_rehearsals())
        self.assertTrue(manager.can_book_rehearsals())
        self.assertTrue(venue_owner.can_book_rehearsals())

    def test_phone_validation(self):
        user = User(
            username='testuser',
            email='test@example.com',
            phone='+375291234567'
        )
        user.full_clean()
        
        user.phone = 'invalid_phone'
        with self.assertRaises(ValidationError):
            user.full_clean()
        
        user.phone = '+3751234567'
        with self.assertRaises(ValidationError):
            user.full_clean()

    def test_telegram_validation(self):
        user = User(
            username='testuser',
            email='test@example.com',
            telegram='@username'
        )
        user.full_clean()
        
        user.telegram = 'username'
        with self.assertRaises(ValidationError):
            user.full_clean()

class RegistrationFormsTests(TestCase):
    def test_viewer_registration_form_valid(self):
        form_data = {
            'username': 'viewer1',
            'email': 'viewer@example.com',
            'password1': 'testpassword123',
            'password2': 'testpassword123',
        }
        form = ViewerRegistrationForm(data=form_data)
        self.assertTrue(form.is_valid())
        user = form.save()
        self.assertEqual(user.username, 'viewer1')
        self.assertEqual(user.role, 'viewer')
        self.assertEqual(user.email, 'viewer@example.com')

    def test_musician_registration_form_valid(self):
        form_data = {
            'username': 'musician1',
            'email': 'musician@example.com',
            'password1': 'testpassword123',
            'password2': 'testpassword123',
            'first_name': 'Иван',
            'last_name': 'Иванов',
            'phone': '+375291234567',
            'instrument': 'guitar',
            'telegram': '@ivanov',
        }
        form = MusicianRegistrationForm(data=form_data)
        self.assertTrue(form.is_valid())
        user = form.save()
        self.assertEqual(user.role, 'musician')

    def test_manager_registration_form_valid(self):
        form_data = {
            'username': 'manager1',
            'email': 'manager@example.com',
            'password1': 'testpassword123',
            'password2': 'testpassword123',
            'first_name': 'Петр',
            'last_name': 'Петров',
            'phone': '+375291234568',
            'instrument': 'vocals',
            'is_manager': True,
            'telegram': '@manager',
        }
        form = MusicianRegistrationForm(data=form_data)
        self.assertTrue(form.is_valid())
        user = form.save()
        self.assertEqual(user.role, 'manager')

    def test_venue_owner_registration_form_valid(self):
        form_data = {
            'username': 'venueowner',
            'email': 'venue@example.com',
            'password1': 'testpassword123',
            'password2': 'testpassword123',
            'first_name': 'Алексей',
            'last_name': 'Сидоров',
            'phone': '+375291234569',
            'venue_name': 'Концертный зал "Весна"',
            'venue_address': 'ул. Музыкальная, д. 1, Минск',
            'telegram': '@venue_owner',
        }
        form = VenueOwnerRegistrationForm(data=form_data)
        self.assertTrue(form.is_valid())
        user = form.save()
        self.assertEqual(user.role, 'venue_owner')

class PasswordResetTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='oldpassword123'
        )
        self.password_reset_url = reverse('password_reset')

    def test_password_reset_flow_complete(self):
        response = self.client.post(self.password_reset_url, {'email': 'testuser@example.com'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(mail.outbox), 1)
        
        reset_email = mail.outbox[0]
        self.assertIn('password-reset-confirm', reset_email.body)