from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages

User = get_user_model()


class AuthenticationTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123',
            'phone': '+375291234567',
            'instrument': 'guitar'
        }
    
    def test_home_page(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Music Manager')
    
    def test_login_page(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Вход в систему')
    
    def test_register_page(self):
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Регистрация')
    
    def test_user_registration(self):
        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'email': 'new@example.com',
            'password1': 'testpass123',
            'password2': 'testpass123',
            'phone': '+375291111111',
            'instrument': 'piano'
        })
        
        if response.status_code == 200:
            print("Form errors:", response.context['form'].errors if 'form' in response.context else 'No form in context')
        else:
            self.assertEqual(response.status_code, 302)

        self.assertTrue(User.objects.filter(username='newuser').exists())
    
    def test_login_logout(self):
        user = User.objects.create_user(
            username='testlogin',
            password='testpass123'
        )
        
        response = self.client.post(reverse('login'), {
            'username': 'testlogin',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 302)

        self.assertTrue('_auth_user_id' in self.client.session)

        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 302)

        self.assertFalse('_auth_user_id' in self.client.session)
    
    def test_profile_access(self):
        user = User.objects.create_user(
            username='profileuser',
            password='testpass123'
        )
        self.client.login(username='profileuser', password='testpass123')

        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Мой профиль')
    
    def test_password_change(self):
        user = User.objects.create_user(
            username='changepass',
            password='oldpass123'
        )
        self.client.login(username='changepass', password='oldpass123')
        
        response = self.client.get(reverse('change_password'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Смена пароля')


class AuthorizationAccessTests(TestCase):
    def test_authenticated_user_redirect_from_login(self):
        user = User.objects.create_user(
            username='loggedin',
            password='testpass123'
        )
        self.client.login(username='loggedin', password='testpass123')
        
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 302)
        
    def test_unauthenticated_profile_access(self):
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/login/?next=/profile/')
    
    def test_user_model_creation(self):
        user = User.objects.create_user(
            username='modeluser',
            email='model@example.com',
            password='testpass123',
            phone='+375292222222',
            instrument='drums'
        )
        
        self.assertEqual(user.username, 'modeluser')
        self.assertEqual(user.email, 'model@example.com')
        self.assertEqual(user.phone, '+375292222222')
        self.assertEqual(user.instrument, 'drums')
        self.assertTrue(user.check_password('testpass123'))


class FormsTests(TestCase):
    def test_login_form_invalid(self):
        response = self.client.post(reverse('login'), {
            'username': '',
            'password': ''
        })
        self.assertEqual(response.status_code, 200)
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(len(messages) > 0)
    
    def test_registration_form_missing_data(self):
        response = self.client.post(reverse('register'), {
            'username': 'incomplete',
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username='incomplete').exists())