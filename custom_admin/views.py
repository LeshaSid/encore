from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from core.models import Musician, Band, Concert, Rehearsal, BandMembership
from core.forms import MusicianForm, BandForm, ConcertForm, BandMembershipForm
from django import forms

def staff_required(user):
    return user.is_staff

# Rehearsal form (not in core.forms, so define inline)
class RehearsalForm(forms.ModelForm):
    class Meta:
        model = Rehearsal
        fields = ['band', 'rehearsal_date', 'duration_minutes', 'location']
        widgets = {
            'rehearsal_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

# Dashboard
@user_passes_test(staff_required)
def admin_dashboard(request):
    counts = {
        'musicians': Musician.objects.count(),
        'bands': Band.objects.count(),
        'concerts': Concert.objects.count(),
        'rehearsals': Rehearsal.objects.count(),
        'membership': BandMembership.objects.count(),
    }
    return render(request, 'custom_admin/dashboard.html', {'counts': counts})

# Generic CRUD helpers
def object_list(request, model, template_name, context_name):
    objects = model.objects.all()
    return render(request, template_name, {context_name: objects})

def object_create(request, form_class, template_name, success_url, title):
    if request.method == 'POST':
        form = form_class(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, f'Запись успешно создана!')
            return redirect(success_url)
    else:
        form = form_class()
    return render(request, template_name, {'form': form, 'title': title})

def object_update(request, pk, model, form_class, template_name, success_url, title):
    obj = get_object_or_404(model, pk=pk)
    if request.method == 'POST':
        form = form_class(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, f'Запись успешно обновлена!')
            return redirect(success_url)
    else:
        form = form_class(instance=obj)
    return render(request, template_name, {'form': form, 'title': title, 'object': obj})

def object_delete(request, pk, model, success_url):
    obj = get_object_or_404(model, pk=pk)
    if request.method == 'POST':
        obj.delete()
        messages.success(request, f'Запись удалена.')
        return redirect(success_url)
    return render(request, 'custom_admin/confirm_delete.html', {'object': obj, 'model_name': model._meta.verbose_name})

# Musicians
@user_passes_test(staff_required)
def musician_list(request):
    return object_list(request, Musician, 'custom_admin/musicians/list.html', 'musicians')

@user_passes_test(staff_required)
def musician_create(request):
    return object_create(request, MusicianForm, 'custom_admin/musicians/form.html', 'custom_admin:musician_list', 'Создать музыканта')

@user_passes_test(staff_required)
def musician_update(request, pk):
    return object_update(request, pk, Musician, MusicianForm, 'custom_admin/musicians/form.html', 'custom_admin:musician_list', 'Редактировать музыканта')

@user_passes_test(staff_required)
def musician_delete(request, pk):
    return object_delete(request, pk, Musician, 'custom_admin:musician_list')

# Bands
@user_passes_test(staff_required)
def band_list(request):
    return object_list(request, Band, 'custom_admin/bands/list.html', 'bands')

@user_passes_test(staff_required)
def band_create(request):
    return object_create(request, BandForm, 'custom_admin/bands/form.html', 'custom_admin:band_list', 'Создать группу')

@user_passes_test(staff_required)
def band_update(request, pk):
    return object_update(request, pk, Band, BandForm, 'custom_admin/bands/form.html', 'custom_admin:band_list', 'Редактировать группу')

@user_passes_test(staff_required)
def band_delete(request, pk):
    return object_delete(request, pk, Band, 'custom_admin:band_list')

# Concerts
@user_passes_test(staff_required)
def concert_list(request):
    return object_list(request, Concert, 'custom_admin/concerts/list.html', 'concerts')

@user_passes_test(staff_required)
def concert_create(request):
    return object_create(request, ConcertForm, 'custom_admin/concerts/form.html', 'custom_admin:concert_list', 'Создать концерт')

@user_passes_test(staff_required)
def concert_update(request, pk):
    return object_update(request, pk, Concert, ConcertForm, 'custom_admin/concerts/form.html', 'custom_admin:concert_list', 'Редактировать концерт')

@user_passes_test(staff_required)
def concert_delete(request, pk):
    return object_delete(request, pk, Concert, 'custom_admin:concert_list')

# Rehearsals
@user_passes_test(staff_required)
def rehearsal_list(request):
    rehearsals = Rehearsal.objects.select_related('band')
    return render(request, 'custom_admin/rehearsals/list.html', {'rehearsals': rehearsals})

@user_passes_test(staff_required)
def rehearsal_create(request):
    return object_create(request, RehearsalForm, 'custom_admin/rehearsals/form.html', 'custom_admin:rehearsal_list', 'Создать репетицию')

@user_passes_test(staff_required)
def rehearsal_update(request, pk):
    return object_update(request, pk, Rehearsal, RehearsalForm, 'custom_admin/rehearsals/form.html', 'custom_admin:rehearsal_list', 'Редактировать репетицию')

@user_passes_test(staff_required)
def rehearsal_delete(request, pk):
    return object_delete(request, pk, Rehearsal, 'custom_admin:rehearsal_list')

# Band Memberships
@user_passes_test(staff_required)
def membership_list(request):
    memberships = BandMembership.objects.select_related('musician', 'band')
    return render(request, 'custom_admin/membership/list.html', {'membership': memberships})

@user_passes_test(staff_required)
def membership_create(request):
    return object_create(request, BandMembershipForm, 'custom_admin/membership/form.html', 'custom_admin:membership_list', 'Создать членство')

@user_passes_test(staff_required)
def membership_update(request, pk):
    return object_update(request, pk, BandMembership, BandMembershipForm, 'custom_admin/membership/form.html', 'custom_admin:membership_list', 'Редактировать членство')

@user_passes_test(staff_required)
def membership_delete(request, pk):
    return object_delete(request, pk, BandMembership, 'custom_admin:membership_list')