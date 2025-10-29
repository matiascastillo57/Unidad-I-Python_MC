# monitoring/device_views.py
"""
Vistas CRUD completas para Device con permisos y SweetAlert2
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseBadRequest
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.db.models import Count, Avg, Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from .models import Device, Zone, Category, Measurement, Alert
from .forms import DeviceForm
from ecoenergy.decorators import permission_required_with_message, ajax_permission_required


def get_user_organization(user):
    """Helper para obtener la organización del usuario"""
    if user.is_superuser:
        return None
    try:
        return user.userprofile.organization
    except:
        return None


@login_required
@permission_required_with_message('monitoring.view_device')
def device_list(request):
    """Lista de dispositivos con filtros, buscador, paginador y ordenamiento"""
    organization = get_user_organization(request.user)
    
    # Base queryset
    if not organization:
        devices = Device.objects.filter(state='ACTIVE')
    else:
        devices = Device.objects.filter(organization=organization, state='ACTIVE')
    
    # Obtener categorías y zonas para filtros
    if organization:
        categories = Category.objects.filter(organization=organization, state='ACTIVE')
        zones = Zone.objects.filter(organization=organization, state='ACTIVE')
    else:
        categories = Category.objects.filter(state='ACTIVE')
        zones = Zone.objects.filter(state='ACTIVE')
    
    # =====================================================================
    # FILTROS ESPECÍFICOS
    # =====================================================================
    selected_category = request.GET.get('category')
    selected_zone = request.GET.get('zone')
    
    if selected_category:
        devices = devices.filter(category_id=selected_category)
    
    if selected_zone:
        devices = devices.filter(zone_id=selected_zone)
    
    # =====================================================================
    # BUSCADOR
    # =====================================================================
    q = request.GET.get('q', '')
    if q:
        devices = devices.filter(
            Q(name__icontains=q) | 
            Q(description__icontains=q)
        )
    
    # =====================================================================
    # ORDENAMIENTO
    # =====================================================================
    sort = request.GET.get('sort', 'name')
    valid_sorts = ['name', '-name', 'max_consumption', '-max_consumption', 'created_at', '-created_at']
    if sort in valid_sorts:
        devices = devices.order_by(sort)
    else:
        devices = devices.order_by('name')
    
    devices = devices.select_related('category', 'zone', 'organization')
    
    # =====================================================================
    # PAGINADOR con tamaño personalizable en sesión
    # =====================================================================
    per_page = request.GET.get('per_page', request.session.get('devices_per_page', '10'))
    try:
        per_page = int(per_page)
        if per_page not in [5, 10, 20, 25, 50]:
            per_page = 10
    except:
        per_page = 10
    
    # Guardar preferencia en sesión
    request.session['devices_per_page'] = per_page
    
    from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
    
    paginator = Paginator(devices, per_page)
    page = request.GET.get('page', 1)
    
    try:
        page_obj = paginator.page(page)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
    
    # Construir querystring para mantener filtros
    querystring = request.GET.copy()
    if 'page' in querystring:
        querystring.pop('page')
    
    context = {
        'page_obj': page_obj,
        'devices': page_obj.object_list,
        'categories': categories,
        'zones': zones,
        'selected_category': selected_category,
        'selected_zone': selected_zone,
        'q': q,
        'sort': sort,
        'per_page': per_page,
        'querystring': querystring.urlencode(),
        'organization': organization,
        'can_add': request.user.has_perm('monitoring.add_device'),
        'can_change': request.user.has_perm('monitoring.change_device'),
        'can_delete': request.user.has_perm('monitoring.delete_device'),
    }
    
    return render(request, 'monitoring/device_list_new.html', context)


@login_required
@permission_required_with_message('monitoring.view_device')
def device_detail(request, pk):
    """Detalle de un dispositivo"""
    organization = get_user_organization(request.user)
    
    if organization:
        device = get_object_or_404(Device, pk=pk, organization=organization, state='ACTIVE')
    else:
        device = get_object_or_404(Device, pk=pk, state='ACTIVE')
    
    # Estadísticas del dispositivo
    measurements = Measurement.objects.filter(device=device, state='ACTIVE').order_by('-measurement_date')[:20]
    alerts = Alert.objects.filter(device=device, state='ACTIVE').order_by('-created_at')[:10]
    
    # Calcular estadísticas
    stats = Measurement.objects.filter(device=device, state='ACTIVE').aggregate(
        avg_consumption=Avg('consumption_value'),
        total_measurements=Count('id')
    )
    
    context = {
        'device': device,
        'measurements': measurements,
        'alerts': alerts,
        'stats': stats,
        'organization': organization,
        'can_change': request.user.has_perm('monitoring.change_device'),
        'can_delete': request.user.has_perm('monitoring.delete_device'),
    }
    
    return render(request, 'monitoring/device_detail_new.html', context)


@login_required
@permission_required_with_message('monitoring.add_device')
def device_create(request):
    """Crear nuevo dispositivo"""
    if request.method == 'POST':
        form = DeviceForm(request.POST, request.FILES, user=request.user)
        
        if form.is_valid():
            device = form.save(commit=False)
            
            # Asignar organización si no es superusuario
            if not request.user.is_superuser:
                try:
                    device.organization = request.user.userprofile.organization
                except:
                    messages.error(request, 'Error: Usuario sin organización asignada')
                    return redirect('device_list')
            
            device.save()
            
            messages.success(
                request,
                f'✅ Dispositivo "{device.name}" creado exitosamente.'
            )
            return redirect('device_detail', pk=device.pk)
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')
    else:
        form = DeviceForm(user=request.user)
    
    context = {
        'form': form,
        'title': 'Nuevo Dispositivo',
        'button_text': 'Crear Dispositivo'
    }
    
    return render(request, 'monitoring/device_form.html', context)


@login_required
@permission_required_with_message('monitoring.change_device')
def device_update(request, pk):
    """Editar dispositivo existente"""
    organization = get_user_organization(request.user)
    
    if organization:
        device = get_object_or_404(Device, pk=pk, organization=organization, state='ACTIVE')
    else:
        device = get_object_or_404(Device, pk=pk, state='ACTIVE')
    
    if request.method == 'POST':
        form = DeviceForm(request.POST, request.FILES, instance=device, user=request.user)
        
        if form.is_valid():
            device = form.save()
            
            messages.success(
                request,
                f'✅ Dispositivo "{device.name}" actualizado exitosamente.'
            )
            return redirect('device_detail', pk=device.pk)
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')
    else:
        form = DeviceForm(instance=device, user=request.user)
    
    context = {
        'form': form,
        'device': device,
        'title': f'Editar Dispositivo: {device.name}',
        'button_text': 'Guardar Cambios'
    }
    
    return render(request, 'monitoring/device_form.html', context)


@login_required
@require_POST
@ajax_permission_required('monitoring.delete_device')
def device_delete_ajax(request, pk):
    """Eliminar dispositivo vía AJAX"""
    if not request.headers.get("x-requested-with") == "XMLHttpRequest":
        return HttpResponseBadRequest("Solo peticiones AJAX")
    
    organization = get_user_organization(request.user)
    
    if organization:
        device = get_object_or_404(Device, pk=pk, organization=organization, state='ACTIVE')
    else:
        device = get_object_or_404(Device, pk=pk, state='ACTIVE')
    
    # Verificar si tiene mediciones
    measurement_count = Measurement.objects.filter(device=device, state='ACTIVE').count()
    
    if measurement_count > 0:
        return JsonResponse({
            'ok': False,
            'message': f'No se puede eliminar "{device.name}" porque tiene {measurement_count} medición(es) registrada(s).'
        })
    
    # Soft delete
    nombre = device.name
    device.state = 'INACTIVE'
    device.save()
    
    return JsonResponse({
        'ok': True,
        'message': f'Dispositivo "{nombre}" eliminado correctamente.'
    })