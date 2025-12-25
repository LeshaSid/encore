import tempfile
import shutil
from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from core.models import Band, Musician, BandMembership

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(prefix='encore_tests_media_')

@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class GroupsAccessTests(TestCase):
    def setUp(self):
        self.client = Client()
        
        self.manager_user = User.objects.create_user(
            username='manager', password='password', is_staff=True, phone='+375000000000'
        )
        
        self.musician_user = User.objects.create_user(
            username='musician', password='password', is_staff=False, phone='+375291111111'
        )
        self.core_musician = Musician.objects.create(
            first_name='John', last_name='Doe', phone='+375291111111', instrument='guitar'
        )
        
        self.guest_user = User.objects.create_user(
            username='guest', password='password', is_staff=False, phone='+375292222222'
        )

        self.band_rock = Band.objects.create(band_name="Rock Band", genre="rock")
        self.band_pop = Band.objects.create(band_name="Pop Band", genre="pop")
        
        BandMembership.objects.create(band=self.band_rock, musician=self.core_musician)

    def tearDown(self):
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_guest_access_denied(self):
        self.client.login(username='guest', password='password')
        response = self.client.get(reverse('groups:band_list'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('home'))

    def test_musician_sees_only_own_bands(self):
        self.client.login(username='musician', password='password')
        response = self.client.get(reverse('groups:band_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Rock Band")
        self.assertNotContains(response, "Pop Band")

    def test_manager_sees_all_bands(self):
        self.client.login(username='manager', password='password')
        response = self.client.get(reverse('groups:band_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Rock Band")
        self.assertContains(response, "Pop Band")

    def test_manager_create_band_with_logo(self):
        self.client.login(username='manager', password='password')
        
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )
        logo = SimpleUploadedFile('test_logo.gif', small_gif, content_type='image/gif')
        
        data = {
            'band_name': 'New Metal Band',
            'genre': 'metal',
            'founded_date': '2023-01-01',
            'logo': logo
        }
        
        response = self.client.post(reverse('groups:band_create'), data, follow=True)
        self.assertEqual(response.status_code, 200)
        
        new_band = Band.objects.get(band_name='New Metal Band')
        self.assertTrue(bool(new_band.logo))
        self.assertTrue('test_logo' in new_band.logo.name)

    def test_crud_access(self):
        self.client.login(username='musician', password='password')
        response = self.client.get(reverse('groups:band_create'))
        self.assertEqual(response.status_code, 403)
        
        self.client.login(username='manager', password='password')
        delete_url = reverse('groups:band_delete', args=[self.band_pop.pk])
        response = self.client.post(delete_url)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Band.objects.filter(pk=self.band_pop.pk).exists())