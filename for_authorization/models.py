from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.utils.translation import gettext_lazy as _

class MusicianUser(AbstractUser):
    
    groups = models.ManyToManyField(
        Group,
        verbose_name=_('groups'),
        blank=True,
        help_text=_('The groups this user belongs to.'),
        related_name="musicianuser_set",
        related_query_name="musicianuser",
    )
    
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name=_('user permissions'),
        blank=True,
        help_text=_('Specific permissions for this user.'),
        related_name="musicianuser_set",
        related_query_name="musicianuser",
    )
    phone = models.CharField(
        max_length=20, 
        blank=True, 
        null=True,
        verbose_name=_('Телефон')
    )
    
    telegram = models.CharField(
        max_length=100, 
        blank=True, 
        null=True,
        verbose_name=_('Telegram')
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
    
    class Meta:
        verbose_name = _('Пользователь-музыкант')
        verbose_name_plural = _('Пользователи-музыканты')
    
    def __str__(self):
        return self.username