from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from .models import Concert
from .utils import get_user_role

class ConcertViewTests(TestCase):
    def setUp(self):
        self.concert = Concert.objects.create(
            concert_title="Mega Rock Fest",
            venue_address="Minsk, Arena",
            concert_date=timezone.now() + timezone.timedelta(days=1)
        )

    def test_upcoming_concerts_view(self):
        url = reverse('concertsshower:upcoming_concerts')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Mega Rock Fest")

    def test_concert_detail_view(self):
        url = reverse('concertsshower:concert_detail', args=[self.concert.concert_id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Minsk, Arena")

class RoleTests(TestCase):
    def setUp(self):
        self.organizer = User.objects.create_user(
            username="organizer",
            password="testpass",
            is_staff=True
        )
        self.musician_user = User.objects.create_user(
            username="musician",
            password="testpass"
        )
        self.viewer_user = User.objects.create_user(
            username="viewer", 
            password="testpass"
        )

    def test_get_user_role_organizer(self):
        role = get_user_role(self.organizer)
        self.assertEqual(role, 'organizer')

    def test_get_user_role_musician(self):
        role = get_user_role(self.musician_user)
        self.assertEqual(role, 'viewer')

class AccessTests(TestCase):
    def setUp(self):
        self.organizer = User.objects.create_user(
            username="organizer",
            password="testpass",
            is_staff=True
        )
        self.musician = User.objects.create_user(
            username="musician",
            password="testpass"
        )
        self.concert = Concert.objects.create(
            concert_title="Test Concert",
            venue_address="Test Address",
            concert_date=timezone.now() + timezone.timedelta(days=1)
        )

    def test_all_concerts_access_organizer(self):
        self.client.login(username='organizer', password='testpass')
        url = reverse('concertsshower:all_concerts')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_all_concerts_access_musician(self):
        self.client.login(username='musician', password='testpass')
        url = reverse('concertsshower:all_concerts')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

    def test_add_concert_access_organizer(self):
        self.client.login(username='organizer', password='testpass')
        url = reverse('concertsshower:add_concert')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)