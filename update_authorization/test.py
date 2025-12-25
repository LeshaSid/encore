import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from .forms import (
    ListenerRegistrationForm,
    MusicianRegistrationForm,
    VenueOwnerRegistrationForm
)

User = get_user_model()

@pytest.mark.django_db
def test_create_listener_user():
    """Тест создания пользователя-зрителя"""
    user = User.objects.create_user(
        username='listener1',
        email='listener@test.com',
        password='testpass123',
        user_type='listener'
    )
    assert user.user_type == 'listener'
    assert user.get_user_type_display() == 'Зритель'

@pytest.mark.django_db
def test_create_musician_with_belarusian_phone():
    """Тест создания музыканта с белорусским номером"""
    user = User.objects.create_user(
        username='musician1',
        email='musician@test.com',
        password='testpass123',
        user_type='musician',
        first_name='Иван',
        last_name='Иванов',
        phone='+375291234567',
        instrument='guitar'
    )
    assert user.phone == '+375291234567'
    assert user.user_type == 'musician'
    assert user.instrument == 'guitar'

@pytest.mark.django_db
def test_create_manager_user():
    """Тест создания менеджера (с галочкой)"""
    user = User.objects.create_user(
        username='manager1',
        email='manager@test.com',
        password='testpass123',
        user_type='manager',
        is_group_manager=True
    )
    assert user.user_type == 'manager'
    assert user.is_group_manager is True

@pytest.mark.django_db
def test_create_venue_owner_user():
    """Тест создания владельца площадки"""
    user = User.objects.create_user(
        username='venueowner1',
        email='venue@test.com',
        password='testpass123',
        user_type='venue_owner',
        venue_name='Rock Cafe',
        venue_address='ул. Пушкина, д. 1'
    )
    assert user.user_type == 'venue_owner'
    assert user.venue_name == 'Rock Cafe'

@pytest.mark.django_db
def test_listener_registration_form_valid():
    """Форма зрителя - валидные данные"""
    form_data = {
        'username': 'newlistener',
        'email': 'newlistener@test.com',
        'password1': 'Testpass123!',
        'password2': 'Testpass123!',
    }
    form = ListenerRegistrationForm(data=form_data)
    assert form.is_valid() is True

@pytest.mark.django_db
def test_musician_registration_form_valid():
    """Форма музыканта - валидные данные"""
    form_data = {
        'username': 'musician1',
        'email': 'musician@test.com',
        'password1': 'Testpass123!',
        'password2': 'Testpass123!',
        'first_name': 'Иван',
        'last_name': 'Иванов',
        'phone': '+375291234567',
        'instrument': 'guitar',
        'telegram': '@ivanov',
        'is_group_manager': False,
    }
    form = MusicianRegistrationForm(data=form_data)
    assert form.is_valid() is True

@pytest.mark.django_db
def test_musician_registration_form_as_manager():
    """Форма музыканта с галочкой 'я менеджер'"""
    form_data = {
        'username': 'manager1',
        'email': 'manager@test.com',
        'password1': 'Testpass123!',
        'password2': 'Testpass123!',
        'first_name': 'Петр',
        'last_name': 'Петров',
        'phone': '+375291234567',
        'instrument': 'other',
        'telegram': '@petrov',
        'is_group_manager': True,
    }
    form = MusicianRegistrationForm(data=form_data)
    assert form.is_valid() is True

@pytest.mark.django_db  
def test_musician_registration_form_invalid_phone():
    """Форма музыканта - невалидный телефон"""
    form_data = {
        'username': 'testmusician',
        'email': 'test@test.com',
        'password1': 'testpassword123',
        'password2': 'testpassword123',
        'first_name': 'Иван',
        'last_name': 'Иванов',
        'phone': '123',
        'instrument': 'guitar',
        'telegram': '@ivanov',
        'is_group_manager': False,
    }
    form = MusicianRegistrationForm(data=form_data)
    assert form.is_valid() is False
    assert 'phone' in form.errors


@pytest.mark.django_db
def test_venue_owner_registration_form_valid():
    """Форма владельца площадки - валидные данные"""
    form_data = {
        'username': 'venueowner1',
        'email': 'venue@test.com',
        'password1': 'Testpass123!',
        'password2': 'Testpass123!',
        'first_name': 'Сергей',
        'last_name': 'Сергеев',
        'phone': '+375295698556',
        'venue_name': 'Jazz Club',
        'venue_address': 'ул. Лермонтова, д. 10',
        'telegram': '@sergeev',
    }
    form = VenueOwnerRegistrationForm(data=form_data)
    assert form.is_valid() is True

@pytest.mark.django_db
def test_home_view(client):
    """Тест главной страницы"""
    response = client.get(reverse('home'))
    assert response.status_code == 200

@pytest.mark.django_db
def test_register_choice_view(client):
    """Тест страницы выбора регистрации"""
    response = client.get(reverse('register_choice'))
    assert response.status_code == 200

@pytest.mark.django_db
def test_password_reset_view(client):
    """Тест страницы восстановления пароля"""
    response = client.get(reverse('password_reset'))
    assert response.status_code == 200
    assert 'Восстановление пароля' in response.content.decode()
