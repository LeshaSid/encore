from django.test import TestCase
from django.urls import reverse
from core.models import Concert
from django.utils import timezone

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