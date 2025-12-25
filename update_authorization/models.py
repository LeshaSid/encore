from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator, EmailValidator

class User(AbstractUser):
    USER_TYPE_CHOICES = [
        ('listener', 'Зритель'),
        ('musician', 'Музыкант'),
        ('manager', 'Менеджер группы'),
        ('venue_owner', 'Владелец площадки/организатор'),
    ]
    
    INSTRUMENT_CHOICES = [
        ('guitar', 'Гитара'),
        ('bass', 'Бас-гитара'),
        ('drums', 'Барабаны'),
        ('keyboard', 'Клавишные'),
        ('vocals', 'Вокал'),
        ('violin', 'Скрипка'),
        ('trumpet', 'Труба'),
        ('saxophone', 'Саксофон'),
        ('other', 'Другой'),
    ]
    
    groups = models.ManyToManyField(
        Group,
        verbose_name=_('groups'),
        blank=True,
        help_text=_('The groups this user belongs to.'),
        related_name="update_authorization_user_set",
        related_query_name="update_authorization_user",
    )
    
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name=_('user permissions'),
        blank=True,
        help_text=_('Specific permissions for this user.'),
        related_name="update_authorization_user_set",
        related_query_name="update_authorization_user",
    )
    
    email = models.EmailField(
        _('email address'),
        validators=[EmailValidator()],
        unique=True,
        error_messages={
            'unique': _("Пользователь с таким email уже существует."),
        }
    )
    
    user_type = models.CharField(
        max_length=20,
        choices=USER_TYPE_CHOICES,
        default='listener',
        verbose_name=_('Тип пользователя')
    )
    
    phone = models.CharField(
        max_length=20,
        validators=[RegexValidator(
            regex=r'^\+375(17|25|29|33|44)\d{7}$',
            message="Номер телефона должен быть в формате: '+37529XXXXXXX' (белорусский номер)"
        )],
        blank=True,
        null=True,
        verbose_name=_('Телефон'),
        help_text=_("Формат: +37529XXXXXXX")
    )
    
    telegram = models.CharField(
        max_length=100,
        validators=[RegexValidator(
            regex=r'^@[A-Za-z0-9_]{5,32}$',
            message="Telegram должен быть в формате: @username"
        )],
        blank=True,
        null=True,
        verbose_name=_('Telegram'),
        help_text=_("Формат: @username")
    )
    
    instrument = models.CharField(
        max_length=50,
        choices=INSTRUMENT_CHOICES,
        blank=True,
        null=True,
        verbose_name=_('Инструмент')
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
    
    is_group_manager = models.BooleanField(
        default=False,
        verbose_name=_('Является менеджером группы')
    )
    
    bio = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('О себе')
    )
    
    class Meta:
        verbose_name = _('Пользователь')
        verbose_name_plural = _('Пользователи')
    
    def __str__(self):
        return f"{self.username} ({self.get_user_type_display()})"