# for_authorization/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator

class MusicianUser(AbstractUser):
    ROLE_CHOICES = [
        ('viewer', 'Зритель'),
        ('musician', 'Музыкант'),
        ('manager', 'Менеджер группы'),
        ('venue_owner', 'Владелец площадки'),
    ]
    
    phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name=_('Телефон'),
        validators=[
            RegexValidator(
                regex=r'^\+375[0-9]{9}$',
                message=_('Phone must be in format +375XXXXXXXXX')
            )
        ]
    )
    
    telegram = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_('Telegram'),
        validators=[
            RegexValidator(
                regex=r'^@.+',
                message=_('Telegram must start with @')
            )
        ]
    )
    
    instrument = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('Инструмент')
    )
    
    bio = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('О себе')
    )
    
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='viewer',
        verbose_name=_('Роль пользователя')
    )
    
    venue_name = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name=_('Название площадки')
    )
    
    venue_address = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Адрес площадки')
    )
    
    class Meta:
        verbose_name = _('Пользователь-музыкант')
        verbose_name_plural = _('Пользователи-музыканты')
    
    def __str__(self):
        return self.username
    
    def is_viewer(self):
        return self.role == 'viewer'
    
    def is_musician(self):
        return self.role == 'musician'
    
    def is_manager(self):
        return self.role == 'manager'
    
    def is_venue_owner(self):
        return self.role == 'venue_owner'
    
    def can_manage_bands(self):
        return self.role in ['manager', 'venue_owner']
    
    def can_book_rehearsals(self):
        return not self.is_viewer()