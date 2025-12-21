from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponseForbidden

from core.models import Band, BandMembership, Musician
from .forms import BandForm, AddMemberForm


@login_required
def band_list(request):
    """Список всех групп с поиском и фильтрацией"""
    search_query = request.GET.get('search', '')
    genre_filter = request.GET.get('genre', '')
    
    bands = Band.objects.all().order_by('band_name')
    
    # Применяем поиск
    if search_query:
        bands = bands.filter(
            Q(band_name__icontains=search_query) |
            Q(genre__icontains=search_query)
        )
    
    # Применяем фильтр по жанру
    if genre_filter:
        bands = bands.filter(genre=genre_filter)
    
    # Пагинация
    paginator = Paginator(bands, 10)  # 10 групп на страницу
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Получаем уникальные жанры для фильтра
    genres = Band.objects.values_list('genre', flat=True).distinct().order_by('genre')
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'genre_filter': genre_filter,
        'genres': genres,
        'total_bands': bands.count(),
    }
    
    return render(request, 'groups/band_list.html', context)


@login_required
def band_create(request):
    """Создание новой группы"""
    if request.method == 'POST':
        form = BandForm(request.POST)
        if form.is_valid():
            band = form.save()
            messages.success(request, f'Группа "{band.band_name}" успешно создана!')
            return redirect('groups:band_list')
    else:
        form = BandForm()
    
    return render(request, 'groups/band_form.html', {
        'form': form,
        'title': 'Создание новой группы',
        'submit_text': 'Создать группу'
    })


@login_required
def band_update(request, pk):
    """Редактирование группы"""
    band = get_object_or_404(Band, pk=pk)
    
    if request.method == 'POST':
        form = BandForm(request.POST, instance=band)
        if form.is_valid():
            band = form.save()
            messages.success(request, f'Группа "{band.band_name}" успешно обновлена!')
            return redirect('groups:band_list')
    else:
        form = BandForm(instance=band)
    
    return render(request, 'groups/band_form.html', {
        'form': form,
        'title': f'Редактирование группы: {band.band_name}',
        'submit_text': 'Сохранить изменения'
    })


@login_required
def band_delete(request, pk):
    """Удаление группы"""
    band = get_object_or_404(Band, pk=pk)
    
    if request.method == 'POST':
        band_name = band.band_name
        band.delete()
        messages.success(request, f'Группа "{band_name}" успешно удалена!')
        return redirect('groups:band_list')
    
    return render(request, 'groups/band_confirm_delete.html', {'band': band})


@login_required
def band_members(request, pk):
    """Управление составом группы"""
    band = get_object_or_404(Band, pk=pk)
    
    # Форма для добавления нового члена
    add_form = AddMemberForm(band=band)
    
    if request.method == 'POST' and 'add_member' in request.POST:
        add_form = AddMemberForm(request.POST, band=band)
        if add_form.is_valid():
            membership = add_form.save(commit=False)
            membership.band = band
            membership.save()
            messages.success(request, f'Музыкант добавлен в группу!')
            return redirect('groups:band_members', pk=band.pk)
    
    # Получаем текущих членов группы
    memberships = BandMembership.objects.filter(band=band).select_related('musician').order_by('-join_date')
    
    context = {
        'band': band,
        'memberships': memberships,
        'add_form': add_form,
    }
    
    return render(request, 'groups/band_members.html', context)


@login_required
def member_remove(request, pk, member_id):
    """Удаление музыканта из группы"""
    band = get_object_or_404(Band, pk=pk)
    membership = get_object_or_404(BandMembership, id=member_id, band=band)
    
    if request.method == 'POST':
        musician_name = str(membership.musician)
        membership.delete()
        messages.success(request, f'Музыкант {musician_name} удален из группы!')
        return redirect('groups:band_members', pk=band.pk)
    
    return render(request, 'groups/member_confirm_remove.html', {
        'band': band,
        'membership': membership
    })