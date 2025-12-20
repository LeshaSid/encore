from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages

from core.models import Musician, Band, Concert, Rehearsal, BandMembership, Performance
from custom_admin.forms import (
    MusicianForm, BandForm, ConcertForm, BandMembershipForm,
    RehearsalForm, PerformanceForm
)


def staff_required(user):
    return user.is_staff


# Dashboard
@user_passes_test(staff_required)
def admin_dashboard(request):
    counts = {
        'musicians': Musician.objects.count(),
        'bands': Band.objects.count(),
        'concerts': Concert.objects.count(),
        'rehearsals': Rehearsal.objects.count(),
        'memberships': BandMembership.objects.count(),
        'performances': Performance.objects.count(),
    }
    return render(request, 'custom_admin/dashboard.html', {'counts': counts})


# Musicians CRUD
@user_passes_test(staff_required)
def musician_list(request):
    musicians = Musician.objects.all().order_by('last_name', 'first_name')
    return render(request, 'custom_admin/musicians/list.html', {'musicians': musicians})


@user_passes_test(staff_required)
def musician_create(request):
    if request.method == 'POST':
        form = MusicianForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Музыкант успешно создан!')
            return redirect('custom_admin:musician_list')
    else:
        form = MusicianForm()
    return render(request, 'custom_admin/musicians/form.html', {
        'form': form,
        'title': 'Создать музыканта'
    })


@user_passes_test(staff_required)
def musician_update(request, pk):
    musician = get_object_or_404(Musician, pk=pk)
    if request.method == 'POST':
        form = MusicianForm(request.POST, instance=musician)
        if form.is_valid():
            form.save()
            messages.success(request, 'Музыкант успешно обновлен!')
            return redirect('custom_admin:musician_list')
    else:
        form = MusicianForm(instance=musician)
    return render(request, 'custom_admin/musicians/form.html', {
        'form': form,
        'title': 'Редактировать музыканта'
    })


@user_passes_test(staff_required)
def musician_delete(request, pk):
    musician = get_object_or_404(Musician, pk=pk)
    if request.method == 'POST':
        musician.delete()
        messages.success(request, 'Музыкант удален!')
        return redirect('custom_admin:musician_list')
    return render(request, 'custom_admin/musicians/confirm_delete.html', {'object': musician})


# Bands CRUD
@user_passes_test(staff_required)
def band_list(request):
    bands = Band.objects.all().order_by('band_name')
    return render(request, 'custom_admin/bands/list.html', {'bands': bands})


@user_passes_test(staff_required)
def band_create(request):
    if request.method == 'POST':
        form = BandForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Группа успешно создана!')
            return redirect('custom_admin:band_list')
    else:
        form = BandForm()
    return render(request, 'custom_admin/bands/form.html', {
        'form': form,
        'title': 'Создать группу'
    })


@user_passes_test(staff_required)
def band_update(request, pk):
    band = get_object_or_404(Band, pk=pk)
    if request.method == 'POST':
        form = BandForm(request.POST, instance=band)
        if form.is_valid():
            form.save()
            messages.success(request, 'Группа успешно обновлена!')
            return redirect('custom_admin:band_list')
    else:
        form = BandForm(instance=band)
    return render(request, 'custom_admin/bands/form.html', {
        'form': form,
        'title': 'Редактировать группу'
    })


@user_passes_test(staff_required)
def band_delete(request, pk):
    band = get_object_or_404(Band, pk=pk)
    if request.method == 'POST':
        band.delete()
        messages.success(request, 'Группа удалена!')
        return redirect('custom_admin:band_list')
    return render(request, 'custom_admin/bands/confirm_delete.html', {'object': band})


# Concerts CRUD
@user_passes_test(staff_required)
def concert_list(request):
    concerts = Concert.objects.all().order_by('-concert_date')
    return render(request, 'custom_admin/concerts/list.html', {'concerts': concerts})


@user_passes_test(staff_required)
def concert_create(request):
    if request.method == 'POST':
        form = ConcertForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Концерт успешно создан!')
            return redirect('custom_admin:concert_list')
    else:
        form = ConcertForm()
    return render(request, 'custom_admin/concerts/form.html', {
        'form': form,
        'title': 'Создать концерт'
    })


@user_passes_test(staff_required)
def concert_update(request, pk):
    concert = get_object_or_404(Concert, pk=pk)
    if request.method == 'POST':
        form = ConcertForm(request.POST, instance=concert)
        if form.is_valid():
            form.save()
            messages.success(request, 'Концерт успешно обновлен!')
            return redirect('custom_admin:concert_list')
    else:
        form = ConcertForm(instance=concert)
    return render(request, 'custom_admin/concerts/form.html', {
        'form': form,
        'title': 'Редактировать концерт'
    })


@user_passes_test(staff_required)
def concert_delete(request, pk):
    concert = get_object_or_404(Concert, pk=pk)
    if request.method == 'POST':
        concert.delete()
        messages.success(request, 'Концерт удален!')
        return redirect('custom_admin:concert_list')
    return render(request, 'custom_admin/concerts/confirm_delete.html', {'object': concert})


# Rehearsals CRUD
@user_passes_test(staff_required)
def rehearsal_list(request):
    rehearsals = Rehearsal.objects.select_related('band').order_by('-rehearsal_date')
    return render(request, 'custom_admin/rehearsals/list.html', {'rehearsals': rehearsals})


@user_passes_test(staff_required)
def rehearsal_create(request):
    if request.method == 'POST':
        form = RehearsalForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Репетиция успешно создана!')
            return redirect('custom_admin:rehearsal_list')
    else:
        form = RehearsalForm()
    return render(request, 'custom_admin/rehearsals/form.html', {
        'form': form,
        'title': 'Создать репетицию'
    })


@user_passes_test(staff_required)
def rehearsal_update(request, pk):
    rehearsal = get_object_or_404(Rehearsal, pk=pk)
    if request.method == 'POST':
        form = RehearsalForm(request.POST, instance=rehearsal)
        if form.is_valid():
            form.save()
            messages.success(request, 'Репетиция успешно обновлена!')
            return redirect('custom_admin:rehearsal_list')
    else:
        form = RehearsalForm(instance=rehearsal)
    return render(request, 'custom_admin/rehearsals/form.html', {
        'form': form,
        'title': 'Редактировать репетицию'
    })


@user_passes_test(staff_required)
def rehearsal_delete(request, pk):
    rehearsal = get_object_or_404(Rehearsal, pk=pk)
    if request.method == 'POST':
        rehearsal.delete()
        messages.success(request, 'Репетиция удалена!')
        return redirect('custom_admin:rehearsal_list')
    return render(request, 'custom_admin/rehearsals/confirm_delete.html', {'object': rehearsal})


# Band Memberships CRUD
@user_passes_test(staff_required)
def membership_list(request):
    memberships = BandMembership.objects.select_related('musician', 'band').order_by('-join_date')
    return render(request, 'custom_admin/membership/list.html', {'memberships': memberships})


@user_passes_test(staff_required)
def membership_create(request):
    if request.method == 'POST':
        form = BandMembershipForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Членство успешно создано!')
            return redirect('custom_admin:membership_list')
    else:
        form = BandMembershipForm()
    return render(request, 'custom_admin/membership/form.html', {
        'form': form,
        'title': 'Создать членство'
    })


@user_passes_test(staff_required)
def membership_update(request, pk):
    membership = get_object_or_404(BandMembership, pk=pk)
    if request.method == 'POST':
        form = BandMembershipForm(request.POST, instance=membership)
        if form.is_valid():
            form.save()
            messages.success(request, 'Членство успешно обновлено!')
            return redirect('custom_admin:membership_list')
    else:
        form = BandMembershipForm(instance=membership)
    return render(request, 'custom_admin/membership/form.html', {
        'form': form,
        'title': 'Редактировать членство'
    })


@user_passes_test(staff_required)
def membership_delete(request, pk):
    membership = get_object_or_404(BandMembership, pk=pk)
    if request.method == 'POST':
        membership.delete()
        messages.success(request, 'Членство удалено!')
        return redirect('custom_admin:membership_list')
    return render(request, 'custom_admin/membership/confirm_delete.html', {'object': membership})


# Performances CRUD (новый функционал)
@user_passes_test(staff_required)
def performance_list(request):
    performances = Performance.objects.select_related('concert', 'band').order_by('concert__concert_date', 'performance_order')
    return render(request, 'custom_admin/performances/list.html', {'performances': performances})


@user_passes_test(staff_required)
def performance_create(request):
    if request.method == 'POST':
        form = PerformanceForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Выступление успешно создано!')
            return redirect('custom_admin:performance_list')
    else:
        form = PerformanceForm()
    return render(request, 'custom_admin/performances/form.html', {
        'form': form,
        'title': 'Создать выступление'
    })


@user_passes_test(staff_required)
def performance_update(request, pk):
    performance = get_object_or_404(Performance, pk=pk)
    if request.method == 'POST':
        form = PerformanceForm(request.POST, instance=performance)
        if form.is_valid():
            form.save()
            messages.success(request, 'Выступление успешно обновлено!')
            return redirect('custom_admin:performance_list')
    else:
        form = PerformanceForm(instance=performance)
    return render(request, 'custom_admin/performances/form.html', {
        'form': form,
        'title': 'Редактировать выступление'
    })


@user_passes_test(staff_required)
def performance_delete(request, pk):
    performance = get_object_or_404(Performance, pk=pk)
    if request.method == 'POST':
        performance.delete()
        messages.success(request, 'Выступление удалено!')
        return redirect('custom_admin:performance_list')
    return render(request, 'custom_admin/performances/confirm_delete.html', {'object': performance})