from django.contrib.auth.models import User
from django.core.cache import cache
from .models import Musician, Band, BandMembership

def get_user_musician(user):
    if not user.is_authenticated:
        return None
    
    if hasattr(user, 'phone') and user.phone:
        try:
            return Musician.objects.get(phone=user.phone)
        except Musician.DoesNotExist:
            pass
    
    if user.username and user.username.isdigit() and len(user.username) >= 10:
        try:
            return Musician.objects.get(phone=user.username)
        except Musician.DoesNotExist:
            pass
    
    if user.email and '@' not in user.email and user.email.isdigit():
        try:
            return Musician.objects.get(phone=user.email)
        except Musician.DoesNotExist:
            pass
    
    return None

def get_user_role(user):
    if not user.is_authenticated:
        return 'viewer'
    
    cache_key = f'user_role_{user.id}'
    cached_role = cache.get(cache_key)
    if cached_role:
        return cached_role
    
    if user.is_staff:
        role = 'organizer'
    
    elif get_user_musician(user):
        role = 'musician'
    
    else:
        role = 'viewer'
    
    cache.set(cache_key, role, 300)
    return role

def is_manager(user):
    return user.is_authenticated and user.is_staff

def check_is_musician(user):
    return get_user_musician(user) is not None

def get_user_bands(user):
    musician = get_user_musician(user)
    if musician:
        memberships = BandMembership.objects.filter(musician=musician).select_related('band')
        return [membership.band for membership in memberships]
    return []

def get_user_primary_band(user):
    bands = get_user_bands(user)
    return bands[0] if bands else None

def can_view_all_concerts(user):
    if not user.is_authenticated:
        return False
    
    return user.is_staff or get_user_musician(user) is not None

def clear_user_role_cache(user):
  
    cache.delete(f'user_role_{user.id}')

def get_user_phone(user):

    if hasattr(user, 'phone'):
        return user.phone
    
    if hasattr(user, 'profile') and hasattr(user.profile, 'phone'):
        return user.profile.phone
    
    if user.username and user.username.isdigit() and len(user.username) >= 10:
        return user.username
    
    return None