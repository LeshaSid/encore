from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.core.files.uploadedfile import SimpleUploadedFile

from core.models import Musician, Band, Concert, Rehearsal, Performance, BandMembership

User = get_user_model()


class CustomAdminAccessTests(TestCase):
    
    def setUp(self):
        self.client = Client()
        

        self.regular_user = User.objects.create_user(
            username='regular',
            password='password123',
            is_staff=False
        )

        self.staff_user = User.objects.create_user(
            username='admin',
            password='admin123',
            is_staff=True
        )

        self.musician = Musician.objects.create(
            first_name='Иван',
            last_name='Петров',
            phone='+375291234567',
            instrument='guitar'
        )
        
        self.band = Band.objects.create(
            band_name='Test Band',
            genre='rock',
            founded_date='2020-01-01'
        )
        
        self.concert = Concert.objects.create(
            concert_title='Test Concert',
            venue_address='Test Address',
            concert_date='2025-01-01 20:00:00'
        )
        
        self.rehearsal = Rehearsal.objects.create(
            band=self.band,
            rehearsal_date='2025-01-01 18:00:00',
            duration_minutes=120,
            location='Test Studio'
        )
        
        self.membership = BandMembership.objects.create(
            band=self.band,
            musician=self.musician,
            join_date='2024-01-01'
        )
        
        self.performance = Performance.objects.create(
            concert=self.concert,
            band=self.band,
            performance_order=1
        )

    def test_dashboard_access_regular_user(self):
        self.client.login(username='regular', password='password123')
        response = self.client.get(reverse('custom_admin:dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/admin/login/?next=/admin-panel/')

    def test_dashboard_access_staff_user(self):
        self.client.login(username='admin', password='admin123')
        response = self.client.get(reverse('custom_admin:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'custom_admin/dashboard.html')
        self.assertContains(response, 'Административная панель')
        self.assertContains(response, 'Музыканты')
        self.assertContains(response, str(Musician.objects.count()))
        self.assertContains(response, str(Band.objects.count()))

    def test_dashboard_context_data(self):
        self.client.login(username='admin', password='admin123')
        response = self.client.get(reverse('custom_admin:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('counts', response.context)
        
        counts = response.context['counts']
        self.assertEqual(counts['musicians'], 1)
        self.assertEqual(counts['bands'], 1)
        self.assertEqual(counts['concerts'], 1)
        self.assertEqual(counts['rehearsals'], 1)
        self.assertEqual(counts['memberships'], 1)
        self.assertEqual(counts['performances'], 1)


class MusicianViewsTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.staff_user = User.objects.create_user(
            username='admin',
            password='admin123',
            is_staff=True
        )
        self.client.login(username='admin', password='admin123')
        
        self.musician_data = {
            'first_name': 'Алексей',
            'last_name': 'Смирнов',
            'phone': '+375292345678',
            'instrument': 'drums',
            'telegram': '@alex_sm'
        }
        
        self.musician = Musician.objects.create(**self.musician_data)

    def test_musician_list_view(self):
        response = self.client.get(reverse('custom_admin:musician_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'custom_admin/musicians/list.html')
        self.assertContains(response, 'Алексей')
        self.assertContains(response, 'Смирнов')
        self.assertContains(response, 'drums')

    def test_musician_create_view_get(self):
        response = self.client.get(reverse('custom_admin:musician_create'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'custom_admin/musicians/form.html')
        self.assertContains(response, 'Создать музыканта')

    def test_musician_create_view_post(self):
        new_musician = {
            'first_name': 'Мария',
            'last_name': 'Иванова',
            'phone': '+375293456789',
            'instrument': 'piano',
            'telegram': '@maria_ivanova'
        }
        
        response = self.client.post(
            reverse('custom_admin:musician_create'),
            new_musician
        )
        
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('custom_admin:musician_list'))
        
        self.assertTrue(Musician.objects.filter(
            first_name='Мария',
            last_name='Иванова'
        ).exists())

    def test_musician_update_view_get(self):
        response = self.client.get(
            reverse('custom_admin:musician_update', args=[self.musician.pk])
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'custom_admin/musicians/form.html')
        self.assertContains(response, 'Редактировать музыканта')
        self.assertContains(response, 'Алексей')

    def test_musician_update_view_post(self):
        """Тест: POST запрос на обновление музыканта"""
        updated_data = {
            'first_name': 'Александр',
            'last_name': 'Смирнов',
            'phone': '+375292345678',
            'instrument': 'bass',
            'telegram': '@alex_bass'
        }
        
        response = self.client.post(
            reverse('custom_admin:musician_update', args=[self.musician.pk]),
            updated_data
        )
        
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('custom_admin:musician_list'))
        
        self.musician.refresh_from_db()
        self.assertEqual(self.musician.first_name, 'Александр')
        self.assertEqual(self.musician.instrument, 'bass')

    def test_musician_delete_view_get(self):
        response = self.client.get(
            reverse('custom_admin:musician_delete', args=[self.musician.pk])
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'custom_admin/musicians/confirm_delete.html')
        self.assertContains(response, 'Подтверждение удаления')
        self.assertContains(response, 'Алексей')

    def test_musician_delete_view_post(self):
        response = self.client.post(
            reverse('custom_admin:musician_delete', args=[self.musician.pk])
        )
        
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('custom_admin:musician_list'))
        
        self.assertFalse(Musician.objects.filter(pk=self.musician.pk).exists())


class BandViewsTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.staff_user = User.objects.create_user(
            username='admin',
            password='admin123',
            is_staff=True
        )
        self.client.login(username='admin', password='admin123')
        
        self.band = Band.objects.create(
            band_name='Rock Stars',
            genre='rock',
            founded_date='2018-05-15'
        )
        
        self.musician = Musician.objects.create(
            first_name='Петр',
            last_name='Сидоров',
            phone='+375294567890',
            instrument='guitar'
        )

    def test_band_list_view(self):
        response = self.client.get(reverse('custom_admin:band_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'custom_admin/bands/list.html')
        self.assertContains(response, 'Rock Stars')
        self.assertContains(response, 'rock')

    def test_band_create_view_post_valid(self):
        new_band = {
            'band_name': 'Jazz Cats',
            'genre': 'jazz',
            'founded_date': '2020-03-20'
        }
        
        response = self.client.post(
            reverse('custom_admin:band_create'),
            new_band
        )
        
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('custom_admin:band_list'))
        self.assertTrue(Band.objects.filter(band_name='Jazz Cats').exists())

    def test_band_create_view_post_invalid(self):
        invalid_band = {
            'band_name': '',
            'genre': 'jazz',
            'founded_date': '2020-03-20'
        }
        
        response = self.client.post(
            reverse('custom_admin:band_create'),
            invalid_band
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'band_name', 'This field is required.')

    def test_band_update_view_post(self):
        updated_data = {
            'band_name': 'Rock Legends',
            'genre': 'hard_rock',
            'founded_date': '2018-05-15'
        }
        
        response = self.client.post(
            reverse('custom_admin:band_update', args=[self.band.pk]),
            updated_data
        )
        
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('custom_admin:band_list'))
        
        self.band.refresh_from_db()
        self.assertEqual(self.band.band_name, 'Rock Legends')
        self.assertEqual(self.band.genre, 'hard_rock')

    def test_band_delete_view(self):
        response = self.client.post(
            reverse('custom_admin:band_delete', args=[self.band.pk])
        )
        
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('custom_admin:band_list'))
        self.assertFalse(Band.objects.filter(pk=self.band.pk).exists())


class ConcertViewsTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.staff_user = User.objects.create_user(
            username='admin',
            password='admin123',
            is_staff=True
        )
        self.client.login(username='admin', password='admin123')
        
        self.concert = Concert.objects.create(
            concert_title='Summer Festival',
            venue_address='Central Park',
            concert_date='2025-07-15 19:00:00'
        )

    def test_concert_list_view(self):
        response = self.client.get(reverse('custom_admin:concert_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'custom_admin/concerts/list.html')
        self.assertContains(response, 'Summer Festival')
        self.assertContains(response, 'Central Park')

    def test_concert_create_view_post(self):
        new_concert = {
            'concert_title': 'Winter Concert',
            'venue_address': 'City Hall',
            'concert_date': '2025-12-20 18:30:00'
        }
        
        response = self.client.post(
            reverse('custom_admin:concert_create'),
            new_concert
        )
        
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('custom_admin:concert_list'))
        self.assertTrue(Concert.objects.filter(concert_title='Winter Concert').exists())

    def test_concert_update_view_post(self):
        updated_data = {
            'concert_title': 'Summer Music Festival',
            'venue_address': 'Central Park, Main Stage',
            'concert_date': '2025-07-15 19:00:00'
        }
        
        response = self.client.post(
            reverse('custom_admin:concert_update', args=[self.concert.pk]),
            updated_data
        )
        
        self.assertEqual(response.status_code, 302)
        self.concert.refresh_from_db()
        self.assertEqual(self.concert.concert_title, 'Summer Music Festival')
        self.assertEqual(self.concert.venue_address, 'Central Park, Main Stage')

    def test_concert_delete_view(self):
        """Тест: удаление концерта"""
        response = self.client.post(
            reverse('custom_admin:concert_delete', args=[self.concert.pk])
        )
        
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Concert.objects.filter(pk=self.concert.pk).exists())


class RehearsalViewsTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.staff_user = User.objects.create_user(
            username='admin',
            password='admin123',
            is_staff=True
        )
        self.client.login(username='admin', password='admin123')
        
        self.band = Band.objects.create(
            band_name='Test Band',
            genre='pop'
        )
        
        self.rehearsal = Rehearsal.objects.create(
            band=self.band,
            rehearsal_date='2025-01-10 17:00:00',
            duration_minutes=90,
            location='Studio A'
        )

    def test_rehearsal_list_view(self):
        response = self.client.get(reverse('custom_admin:rehearsal_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'custom_admin/rehearsals/list.html')
        self.assertContains(response, 'Studio A')
        self.assertContains(response, '90 мин.')

    def test_rehearsal_create_view_post_valid(self):
        new_rehearsal = {
            'band': self.band.pk,
            'rehearsal_date': '2025-01-12 18:00:00',
            'duration_minutes': 120,
            'location': 'Studio B'
        }
        
        response = self.client.post(
            reverse('custom_admin:rehearsal_create'),
            new_rehearsal
        )
        
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('custom_admin:rehearsal_list'))
        
        self.assertTrue(Rehearsal.objects.filter(
            location='Studio B',
            duration_minutes=120
        ).exists())

    def test_rehearsal_create_view_post_invalid_duration(self):
        invalid_rehearsal = {
            'band': self.band.pk,
            'rehearsal_date': '2025-01-12 18:00:00',
            'duration_minutes': 5,
            'location': 'Studio B'
        }
        
        response = self.client.post(
            reverse('custom_admin:rehearsal_create'),
            invalid_rehearsal
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response, 'form', 'duration_minutes',
            'Минимальная продолжительность репетиции - 15 минут'
        )

    def test_rehearsal_update_view_post(self):
        updated_data = {
            'band': self.band.pk,
            'rehearsal_date': '2025-01-10 18:00:00', 
            'duration_minutes': 120, 
            'location': 'Main Studio' 
        }
        
        response = self.client.post(
            reverse('custom_admin:rehearsal_update', args=[self.rehearsal.pk]),
            updated_data
        )
        
        self.assertEqual(response.status_code, 302)
        self.rehearsal.refresh_from_db()
        self.assertEqual(self.rehearsal.duration_minutes, 120)
        self.assertEqual(self.rehearsal.location, 'Main Studio')

    def test_rehearsal_delete_view(self):
        response = self.client.post(
            reverse('custom_admin:rehearsal_delete', args=[self.rehearsal.pk])
        )
        
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Rehearsal.objects.filter(pk=self.rehearsal.pk).exists())


class PerformanceViewsTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.staff_user = User.objects.create_user(
            username='admin',
            password='admin123',
            is_staff=True
        )
        self.client.login(username='admin', password='admin123')
        
        self.band = Band.objects.create(
            band_name='Performance Band',
            genre='rock'
        )
        
        self.concert = Concert.objects.create(
            concert_title='Test Festival',
            venue_address='Test Venue'
        )
        
        self.performance = Performance.objects.create(
            concert=self.concert,
            band=self.band,
            performance_order=1
        )

    def test_performance_list_view(self):
        response = self.client.get(reverse('custom_admin:performance_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'custom_admin/performances/list.html')
        self.assertContains(response, 'Performance Band')
        self.assertContains(response, 'Test Festival')

    def test_performance_create_view_post(self):
        concert2 = Concert.objects.create(
            concert_title='Another Concert',
            venue_address='Another Venue'
        )
        
        band2 = Band.objects.create(
            band_name='Second Band',
            genre='jazz'
        )
        
        new_performance = {
            'concert': concert2.pk,
            'band': band2.pk,
            'performance_order': 2
        }
        
        response = self.client.post(
            reverse('custom_admin:performance_create'),
            new_performance
        )
        
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('custom_admin:performance_list'))
        
        self.assertTrue(Performance.objects.filter(
            concert=concert2,
            band=band2,
            performance_order=2
        ).exists())

    def test_performance_update_view_post(self):
        new_band = Band.objects.create(
            band_name='Updated Band',
            genre='pop'
        )
        
        updated_data = {
            'concert': self.concert.pk,
            'band': new_band.pk,
            'performance_order': 3
        }
        
        response = self.client.post(
            reverse('custom_admin:performance_update', args=[self.performance.pk]),
            updated_data
        )
        
        self.assertEqual(response.status_code, 302)
        self.performance.refresh_from_db()
        self.assertEqual(self.performance.band, new_band)
        self.assertEqual(self.performance.performance_order, 3)

    def test_performance_delete_view(self):
        response = self.client.post(
            reverse('custom_admin:performance_delete', args=[self.performance.pk])
        )
        
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Performance.objects.filter(pk=self.performance.pk).exists())


class MembershipViewsTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.staff_user = User.objects.create_user(
            username='admin',
            password='admin123',
            is_staff=True
        )
        self.client.login(username='admin', password='admin123')
        
        self.musician = Musician.objects.create(
            first_name='Иван',
            last_name='Членов',
            phone='+375295678901',
            instrument='bass'
        )
        
        self.band = Band.objects.create(
            band_name='Membership Test Band',
            genre='metal'
        )
        
        self.membership = BandMembership.objects.create(
            band=self.band,
            musician=self.musician,
            join_date='2024-02-01'
        )

    def test_membership_list_view(self):
        response = self.client.get(reverse('custom_admin:membership_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'custom_admin/membership/list.html')
        self.assertContains(response, 'Иван Членов')
        self.assertContains(response, 'Membership Test Band')

    def test_membership_create_view_post(self):
        new_musician = Musician.objects.create(
            first_name='Петр',
            last_name='Новый',
            phone='+375296789012',
            instrument='guitar'
        )
        
        new_membership = {
            'band': self.band.pk,
            'musician': new_musician.pk,
            'join_date': '2024-03-01'
        }
        
        response = self.client.post(
            reverse('custom_admin:membership_create'),
            new_membership
        )
        
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('custom_admin:membership_list'))
        
        self.assertTrue(BandMembership.objects.filter(
            band=self.band,
            musician=new_musician
        ).exists())

    def test_membership_create_view_post_duplicate(self):
        duplicate_membership = {
            'band': self.band.pk,
            'musician': self.musician.pk,
            'join_date': '2024-03-01'
        }
        
        response = self.client.post(
            reverse('custom_admin:membership_create'),
            duplicate_membership
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response, 'form', '__all__',
            'Band membership with this Band and Musician already exists.'
        )

    def test_membership_update_view_post(self):
        """Тест: обновление членства"""
        updated_data = {
            'band': self.band.pk,
            'musician': self.musician.pk,
            'join_date': '2024-01-15'
        }
        
        response = self.client.post(
            reverse('custom_admin:membership_update', args=[self.membership.pk]),
            updated_data
        )
        
        self.assertEqual(response.status_code, 302)
        self.membership.refresh_from_db()
        self.assertEqual(str(self.membership.join_date), '2024-01-15')

    def test_membership_delete_view(self):
        response = self.client.post(
            reverse('custom_admin:membership_delete', args=[self.membership.pk])
        )
        
        self.assertEqual(response.status_code, 302)
        self.assertFalse(BandMembership.objects.filter(pk=self.membership.pk).exists())


class NavigationAndTemplateTests(TestCase):
    
    def setUp(self):
        self.client = Client()
        self.staff_user = User.objects.create_user(
            username='admin',
            password='admin123',
            is_staff=True
        )
        self.client.login(username='admin', password='admin123')
    
    def test_admin_base_template(self):
        response = self.client.get(reverse('custom_admin:dashboard'))
        self.assertEqual(response.status_code, 200)
        
        self.assertContains(response, 'Главная')
        self.assertContains(response, 'Музыканты')
        self.assertContains(response, 'Группы')
        self.assertContains(response, 'Концерты')
        self.assertContains(response, 'Выступления')
        self.assertContains(response, 'Репетиции')
        self.assertContains(response, 'Членства')
    
    def test_dashboard_template_content(self):
        response = self.client.get(reverse('custom_admin:dashboard'))
        
        self.assertContains(response, 'card text-bg-primary')
        self.assertContains(response, 'card text-bg-success')
        self.assertContains(response, 'card text-bg-warning')
        self.assertContains(response, 'card text-bg-info')
        self.assertContains(response, 'card text-bg-secondary')
        self.assertContains(response, 'card text-bg-dark')
        
        self.assertContains(response, 'Новый музыкант')
        self.assertContains(response, 'Новая группа')
        self.assertContains(response, 'Новый концерт')
        self.assertContains(response, 'Новое выступление')
        self.assertContains(response, 'Новая репетиция')
        self.assertContains(response, 'Новое членство')
    
    def test_form_templates_have_required_fields(self):
        urls_to_test = [
            ('custom_admin:musician_create', 'first_name'),
            ('custom_admin:band_create', 'band_name'),
            ('custom_admin:concert_create', 'concert_title'),
            ('custom_admin:rehearsal_create', 'location'),
        ]
        
        for url_name, field_name in urls_to_test:
            response = self.client.get(reverse(url_name))
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, field_name)
            self.assertContains(response, 'required')


class ErrorHandlingTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.staff_user = User.objects.create_user(
            username='admin',
            password='admin123',
            is_staff=True
        )
        self.client.login(username='admin', password='admin123')
    
    def test_nonexistent_object_update(self):
        """Тест: попытка редактирования несуществующего объекта"""
        response = self.client.get(reverse('custom_admin:musician_update', args=[9999]))
        self.assertEqual(response.status_code, 404)
    
    def test_nonexistent_object_delete(self):
        """Тест: попытка удаления несуществующего объекта"""
        response = self.client.post(reverse('custom_admin:band_delete', args=[9999]))
        self.assertEqual(response.status_code, 404)
    
    def test_invalid_post_data(self):
        """Тест: отправка невалидных данных в форму"""
        invalid_data = {
            'band_name': '',
            'genre': 'rock',
            'founded_date': 'invalid_date'
        }
        
        response = self.client.post(
            reverse('custom_admin:band_create'),
            invalid_data
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'band_name', 'This field is required.')
        self.assertFormError(response, 'form', 'founded_date', 'Enter a valid date.')


class MessageDisplayTests(TestCase):
    
    def setUp(self):
        self.client = Client()
        self.staff_user = User.objects.create_user(
            username='admin',
            password='admin123',
            is_staff=True
        )
        self.client.login(username='admin', password='admin123')
        
        self.musician = Musician.objects.create(
            first_name='Test',
            last_name='Musician',
            phone='+375290000000',
            instrument='guitar'
        )
    
    def test_success_message_on_create(self):
        new_musician = {
            'first_name': 'New',
            'last_name': 'Musician',
            'phone': '+375291111111',
            'instrument': 'piano'
        }
        
        response = self.client.post(
            reverse('custom_admin:musician_create'),
            new_musician,
            follow=True
        )
        
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(str(messages_list[0]), 'Музыкант успешно создан!')
        self.assertEqual(messages_list[0].tags, 'success')
    
    def test_success_message_on_update(self):
        """Тест: сообщение об успешном обновлении"""
        updated_data = {
            'first_name': 'Updated',
            'last_name': 'Musician',
            'phone': '+375290000000',
            'instrument': 'bass'
        }
        
        response = self.client.post(
            reverse('custom_admin:musician_update', args=[self.musician.pk]),
            updated_data,
            follow=True
        )
        
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(str(messages_list[0]), 'Музыкант успешно обновлен!')
        self.assertEqual(messages_list[0].tags, 'success')
    
    def test_success_message_on_delete(self):
        response = self.client.post(
            reverse('custom_admin:musician_delete', args=[self.musician.pk]),
            follow=True
        )
        
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(str(messages_list[0]), 'Музыкант удален!')
        self.assertEqual(messages_list[0].tags, 'success')