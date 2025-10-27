# monitoring/device_views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Device, Zone
from .forms import DeviceForm

def device_list(request):
    """Lista todos los dispositivos con buscador, paginador y ordenamiento"""
    
    # 1. BÚSQUEDA
    q = request.GET.get('q', '')
    devices = Device.objects.select_related('zone')
    
    if q:
        devices = devices.filter(
            Q(name__icontains=q) | 
            Q(description__icontains=q) |
            Q(device_type__icontains=q) |
            Q(zone__name__icontains=q)
        )
    
    # 2. ORDENAMIENTO
    sort = request.GET.get('sort', 'name')
    valid_sorts = ['name', '-name', 'device_type', '-device_type', 'zone__name', '-zone__name', 'created_at', '-created_at']
    
    if sort in valid_sorts:
        devices = devices.order_by(sort)
    else:
        devices = devices.order_by('name')
    
    # 3. PAGINACIÓN (con opción de items por página)
    per_page = request.GET.get('per_page', request.session.get('per_page', 10))
    
    # Guardar preferencia en sesión (caché)
    try:
        per_page = int(per_page)
        if per_page in [5, 10, 25, 50]:
            request.session['per_page'] = per_page
    except (ValueError, TypeError):
        per_page = 10
    
    paginator = Paginator(devices, per_page)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    # 4. QUERYSTRING para mantener parámetros en paginación
    querystring = request.GET.copy()
    if 'page' in querystring:
        querystring.pop('page')
    
    context = {
        'page_obj': page_obj,
        'q': q,
        'sort': sort,
        'per_page': per_page,
        'querystring': querystring.urlencode(),
        'title': 'Dispositivos'
    }
    return render(request, 'monitoring/device_list.html', context)


def device_create(request):
    """Crea un nuevo dispositivo"""
    if request.method == 'POST':
        form = DeviceForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Dispositivo creado exitosamente.')
            return redirect('device_list')
    else:
        form = DeviceForm()
    
    context = {
        'form': form,
        'title': 'Crear Dispositivo',
        'action': 'Crear'
    }
    return render(request, 'monitoring/device_form.html', context)


def device_detail(request, pk):
    """Detalle de un dispositivo"""
    device = get_object_or_404(Device, pk=pk)
    measurements = device.measurements.all().order_by('-timestamp')[:10]
    
    context = {
        'device': device,
        'measurements': measurements,
        'title': f'Dispositivo: {device.name}'
    }
    return render(request, 'monitoring/device_detail.html', context)


def device_update(request, pk):
    """Actualiza un dispositivo"""
    device = get_object_or_404(Device, pk=pk)
    
    if request.method == 'POST':
        form = DeviceForm(request.POST, instance=device)
        if form.is_valid():
            form.save()
            messages.success(request, 'Dispositivo actualizado exitosamente.')
            return redirect('device_list')
    else:
        form = DeviceForm(instance=device)
    
    context = {
        'form': form,
        'device': device,
        'title': 'Editar Dispositivo',
        'action': 'Actualizar'
    }
    return render(request, 'monitoring/device_form.html', context)


def device_delete_ajax(request, pk):
    """Elimina un dispositivo (AJAX)"""
    if request.method == 'POST':
        device = get_object_or_404(Device, pk=pk)
        device_name = device.name
        device.delete()
        return JsonResponse({
            'success': True,
            'message': f'Dispositivo "{device_name}" eliminado exitosamente.'
        })
    return JsonResponse({'success': False, 'message': 'Método no permitido.'}, status=405)