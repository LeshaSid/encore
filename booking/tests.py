from django.test import TestCase, Client
from django.urls import reverse
from core.models import Band, Rehearsal
from django.utils import timezone

class BookingViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.band = Band.objects.create(
            band_name="Test Band",
            genre="rock",
            founded_date=timezone.now().date()
        )
        self.url = reverse('book')

    def test_book_page_status_code(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_rehearsal_creation(self):
        data = {
            'band': self.band.band_id,
            'rehearsal_date': '2025-12-25T14:00',
            'duration_minutes': 60,
            'location': 'Main Studio'
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Rehearsal.objects.filter(location='Main Studio').exists())