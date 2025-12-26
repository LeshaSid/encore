# for_authorization/tests.py
from django.test import TestCase, Client
from django.urls import reverse
from django.core import mail
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from for_authorization.forms import (
    ViewerRegistrationForm,
    MusicianRegistrationForm,
    VenueOwnerRegistrationForm
)
from for_authorization.models import MusicianUser

User = get_user_model()

class UserModelTests(TestCase):
    def test_role_methods(self):
        """Тест методов проверки ролей"""
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

    def test_phone_validation(self):
        """Тест валидации телефона"""
        user = User(
            username='testuser',
            email='test@example.com',
            phone='+375291234567'
        )
        user.full_clean()  # Не должно вызвать исключение
        
        user.phone = 'invalid_phone'
        with self.assertRaises(ValidationError):
            user.full_clean()
        
        user.phone = '+3751234567'
        with self.assertRaises(ValidationError):
            user.full_clean()

    def test_telegram_validation(self):
        """Тест валидации Telegram"""
        user = User(
            username='testuser',
            email='test@example.com',
            telegram='@username'
        )
        user.full_clean()  # Не должно вызвать исключение
        
        user.telegram = 'username'  # без @
        with self.assertRaises(ValidationError):
            user.full_clean()

class RegistrationFormsTests(TestCase):
    def test_viewer_registration_form_valid(self):
        """Тест валидной формы зрителя"""
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

    def test_viewer_registration_form_invalid_password(self):
        """Тест невалидного пароля"""
        form_data = {
            'username': 'viewer2',
            'email': 'viewer2@example.com',
            'password1': 'short',
            'password2': 'short',
        }
        form = ViewerRegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)

    def test_musician_registration_form_valid(self):
        """Тест валидной формы музыканта"""
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
        self.assertEqual(user.first_name, 'Иван')
        self.assertEqual(user.phone, '+375291234567')
        self.assertEqual(user.instrument, 'guitar')
        self.assertEqual(user.telegram, '@ivanov')

    def test_manager_registration_form_valid(self):
        """Тест валидной формы менеджера"""
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
        self.assertEqual(user.first_name, 'Петр')

    def test_musician_registration_form_invalid_phone(self):
        """Тест невалидного телефона"""
        form_data = {
            'username': 'musician2',
            'email': 'musician2@example.com',
            'password1': 'testpassword123',
            'password2': 'testpassword123',
            'first_name': 'Иван',
            'last_name': 'Иванов',
            'phone': 'invalid_phone',
            'instrument': 'guitar',
        }
        form = MusicianRegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('phone', form.errors)

    def test_venue_owner_registration_form_valid(self):
        """Тест валидной формы владельца площадки"""
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
        self.assertEqual(user.venue_name, 'Концертный зал "Весна"')
        self.assertEqual(user.venue_address, 'ул. Музыкальная, д. 1, Минск')

    def test_venue_owner_registration_form_missing_fields(self):
        """Тест отсутствия обязательных полей"""
        form_data = {
            'username': 'venueowner2',
            'email': 'venue2@example.com',
            'password1': 'testpassword123',
            'password2': 'testpassword123',
            'first_name': 'Алексей',
            'last_name': 'Сидоров',
            'phone': '+375291234569',
            # Отсутствуют venue_name и venue_address
        }
        form = VenueOwnerRegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('venue_name', form.errors)
        self.assertIn('venue_address', form.errors)

class RegistrationViewsTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.register_url = reverse('register')

    def test_viewer_registration_view(self):
        """Тест регистрации зрителя через представление"""
        response = self.client.get(self.register_url + '?type=viewer')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Зритель')
        
        form_data = {
            'form_type': 'viewer',
            'username': 'testviewer',
            'email': 'testviewer@example.com',
            'password1': 'testpassword123',
            'password2': 'testpassword123',
        }
        response = self.client.post(self.register_url, form_data)
        self.assertEqual(response.status_code, 302)  # Редирект после успешной регистрации
        user = User.objects.get(username='testviewer')
        self.assertEqual(user.role, 'viewer')

    def test_musician_registration_view(self):
        """Тест регистрации музыканта через представление"""
        form_data = {
            'form_type': 'musician',
            'username': 'testmusician',
            'email': 'testmusician@example.com',
            'password1': 'testpassword123',
            'password2': 'testpassword123',
            'first_name': 'Test',
            'last_name': 'Musician',
            'phone': '+375291234567',
            'instrument': 'guitar',
            'telegram': '@test',
        }
        response = self.client.post(self.register_url, form_data)
        self.assertEqual(response.status_code, 302)
        user = User.objects.get(username='testmusician')
        self.assertEqual(user.role, 'musician')
        self.assertEqual(user.phone, '+375291234567')

    def test_manager_registration_view(self):
        """Тест регистрации менеджера через представление"""
        form_data = {
            'form_type': 'musician',
            'username': 'testmanager',
            'email': 'testmanager@example.com',
            'password1': 'testpassword123',
            'password2': 'testpassword123',
            'first_name': 'Test',
            'last_name': 'Manager',
            'phone': '+375291234568',
            'instrument': 'vocals',
            'is_manager': 'on',  # Чекбокс включен
            'telegram': '@manager',
        }
        response = self.client.post(self.register_url, form_data)
        self.assertEqual(response.status_code, 302)
        user = User.objects.get(username='testmanager')
        self.assertEqual(user.role, 'manager')

    def test_venue_owner_registration_view(self):
        """Тест регистрации владельца площадки через представление"""
        form_data = {
            'form_type': 'venue_owner',
            'username': 'testvenue',
            'email': 'testvenue@example.com',
            'password1': 'testpassword123',
            'password2': 'testpassword123',
            'first_name': 'Test',
            'last_name': 'Venue',
            'phone': '+375291234569',
            'venue_name': 'Test Venue',
            'venue_address': 'Test Address',
            'telegram': '@venue',
        }
        response = self.client.post(self.register_url, form_data)
        self.assertEqual(response.status_code, 302)
        user = User.objects.get(username='testvenue')
        self.assertEqual(user.role, 'venue_owner')
        self.assertEqual(user.venue_name, 'Test Venue')

class PasswordResetTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='oldpassword123'
        )
        self.password_reset_url = reverse('password_reset')
        self.password_reset_done_url = reverse('password_reset_done')

    def test_password_reset_view(self):
        """Тест страницы сброса пароля"""
        response = self.client.get(self.password_reset_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Восстановление пароля')

    def test_password_reset_form_valid(self):
        """Тест отправки формы сброса пароля"""
        form_data = {
            'email': 'testuser@example.com'
        }
        response = self.client.post(self.password_reset_url, form_data)
        self.assertEqual(response.status_code, 302)  # Редирект на done
        # Проверяем, что письмо было отправлено
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('testuser@example.com', mail.outbox[0].to)
        self.assertIn('Encore', mail.outbox[0].subject)

    def test_password_reset_form_invalid_email(self):
        """Тест отправки формы с несуществующим email"""
        form_data = {
            'email': 'nonexistent@example.com'
        }
        response = self.client.post(self.password_reset_url, form_data)
        # Django не сообщает пользователю, существует email или нет
        # Поэтому форма все равно считается валидной
        self.assertEqual(response.status_code, 302)

    def test_password_reset_flow_complete(self):
        """Полный тест процесса сброса пароля"""
        # 1. Запрос сброса пароля
        self.client.post(self.password_reset_url, {'email': 'testuser@example.com'})
        
        # 2. Получаем ссылку из письма
        reset_email = mail.outbox[0]
        self.assertIn('password-reset-confirm', reset_email.body)
        
        # 3. Находим URL для сброса пароля
        from django.contrib.auth.tokens import default_token_generator
        from django.utils.encoding import force_bytes
        from django.utils.http import urlsafe_base64_encode
        
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        token = default_token_generator.make_token(self.user)
        confirm_url = reverse('password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
        
        # 4. Переходим по ссылке подтверждения
        response = self.client.get(confirm_url)
        self.assertEqual(response.status_code, 302)  # Перенаправление на форму ввода пароля
        
        # 5. Получаем окончательный URL и устанавливаем новый пароль
        final_url = response.url
        response = self.client.get(final_url)
        self.assertContains(response, 'Введите новый пароль')
        
        form_data = {
            'new_password1': 'newpassword123',
            'new_password2': 'newpassword123'
        }
        response = self.client.post(final_url, form_data)
        self.assertEqual(response.status_code, 302)  # Редирект на complete
        
        # 6. Проверяем, что пароль изменился
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('newpassword123'))