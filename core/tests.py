# core/tests.py
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Venue, RehearsalSlot
from rehearsals.models import Booking
from for_authorization.models import MusicianUser

User = get_user_model()

class CoreViewsTests(TestCase):
    def setUp(self):
        self.client = Client()
        
        self.viewer = User.objects.create_user(
            username='viewer',
            password='viewerpass',
            role='viewer'
        )
        
        self.musician = User.objects.create_user(
            username='musician',
            password='musicianpass',
            role='musician',
            phone='+375291111111'
        )
        
        self.venue = Venue.objects.create(
            name="Тестовая площадка",
            address="Тестовый адрес",
            contact_phone="+375291234567"
        )
        
        self.slot = RehearsalSlot.objects.create(
            venue=self.venue,
            start_time="2025-12-27T10:00:00",
            end_time="2025-12-27T12:00:00",
            price=50.00
        )
    
    def test_home_view(self):
        self.client.login(username='musician', password='musicianpass')
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/home.html')
    
    def test_venue_list_view(self):
        self.client.login(username='musician', password='musicianpass')
        response = self.client.get(reverse('venue_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Тестовая площадка")
    
    def test_venue_detail_view(self):
        self.client.login(username='musician', password='musicianpass')
        response = self.client.get(reverse('venue_detail', args=[self.venue.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Тестовая площадка")
        self.assertContains(response, "10:00 - 12:00")
    
    def test_book_rehearsal_viewer_denied(self):
        self.client.login(username='viewer', password='viewerpass')
        response = self.client.get(reverse('book_rehearsal', args=[self.slot.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('home'))
        messages = list(response.wsgi_request._messages)
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Зрители не могут бронировать репетиции")
    
    def test_book_rehearsal_musician_allowed(self):
        self.client.login(username='musician', password='musicianpass')
        response = self.client.get(reverse('book_rehearsal', args=[self.slot.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/book_rehearsal.html')
    
    def test_book_rehearsal_post(self):
        self.client.login(username='musician', password='musicianpass')
        form_data = {
            'instrument': 'guitar',
            'band_name': 'Тестовая группа',
            'contact_phone': '+375291111111'
        }
        response = self.client.post(reverse('book_rehearsal', args=[self.slot.pk]), form_data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(RehearsalSlot.objects.get(pk=self.slot.pk).is_booked)
        self.assertEqual(Booking.objects.count(), 1)
        messages = list(response.wsgi_request._messages)
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Репетиция успешно забронирована!")