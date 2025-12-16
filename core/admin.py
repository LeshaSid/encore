from django.contrib import admin
from .models import Musician, Band, Concert, Performance, Rehearsal, BandMembership


@admin.register(Musician)
class MusicianAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'phone', 'instrument', 'telegram')
    list_filter = ('instrument',)
    search_fields = ('first_name', 'last_name', 'phone', 'instrument')


@admin.register(Band)
class BandAdmin(admin.ModelAdmin):
    list_display = ('band_name', 'genre', 'founded_date')
    list_filter = ('genre', 'founded_date')
    search_fields = ('band_name', 'genre')


@admin.register(Concert)
class ConcertAdmin(admin.ModelAdmin):
    list_display = ('concert_title', 'venue_address', 'concert_date')
    list_filter = ('concert_date',)
    search_fields = ('concert_title', 'venue_address')
    date_hierarchy = 'concert_date'


@admin.register(Performance)
class PerformanceAdmin(admin.ModelAdmin):
    list_display = ('concert', 'band', 'performance_order')
    list_filter = ('concert', 'band')
    autocomplete_fields = ['concert', 'band']


@admin.register(Rehearsal)
class RehearsalAdmin(admin.ModelAdmin):
    list_display = ('band', 'rehearsal_date', 'duration_minutes', 'location')
    list_filter = ('band', 'rehearsal_date')
    search_fields = ('location', 'band__band_name')
    date_hierarchy = 'rehearsal_date'


@admin.register(BandMembership)
class BandMembershipAdmin(admin.ModelAdmin):
    list_display = ('musician', 'band', 'join_date')
    list_filter = ('band', 'join_date')
    search_fields = ('musician__first_name', 'musician__last_name', 'band__band_name')
    autocomplete_fields = ['musician', 'band']
