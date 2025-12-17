# for_authorization/apps.py
from django.apps import AppConfig


class ForAuthorizationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'for_authorization'
    verbose_name = 'Авторизация'