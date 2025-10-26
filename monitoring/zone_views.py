# monitoring/zone_views.py
"""
Vistas CRUD completas para Zone con permisos y SweetAlert2
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseBadRequest
from django.contrib import messages
from django.views.decorators.http import require_POST

from django.db.models import Count, Q

from .models import Zone, Device, models

from django.db.models import Count

from .models import Zone, Device

from .forms import ZoneForm
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
def zona_list(request):
    """
    Lista todas las zonas de la organización del usuario
    Con contador de dispositivos por zona
    """
    organization = get_user_organization(request.user)
    
    # Contador de visitas en sesión (ejemplo de uso de sesión)
    visitas_zonas = request.session.get('visitas_zonas', 0)
    request.session['visitas_zonas'] = visitas_zonas + 1
    
    if not organization:
        # Superusuario ve todas
        zones = Zone.objects.filter(state='ACTIVE')
    else:
        # Usuario normal ve solo de su organización
        zones = Zone.objects.filter(
            organization=organization,
            state='ACTIVE'
        )
    
    # Anotar con conteo de dispositivos
    zones = zones.annotate(
        device_count=Count('device', filter=models.Q(device__state='ACTIVE'))
    ).select_related('organization').order_by('name')
    
    context = {
        'zones': zones,
        'organization': organization,
        'visitas_zonas': visitas_zonas,
        # Permisos para el template
        'can_add': request.user.has_perm('monitoring.add_zone'),
        'can_change': request.user.has_perm('monitoring.change_zone'),
        'can_delete': request.user.has_perm('monitoring.delete_zone'),
    }
    
    return render(request, 'monitoring/zona_list.html', context)


@login_required
@permission_required_with_message('monitoring.view_zone')
def zona_detail(request, pk):
    """
    Detalle de una zona con sus dispositivos
    """
    organization = get_user_organization(request.user)
    
    # Obtener la zona
    if organization:
        zone = get_object_or_404(Zone, pk=pk, organization=organization, state='ACTIVE')
    else:
        zone = get_object_or_404(Zone, pk=pk, state='ACTIVE')
    
    # Obtener dispositivos de la zona
    devices = Device.objects.filter(
        zone=zone,
        state='ACTIVE'
    ).select_related('category').order_by('name')
    
    context = {
        'zone': zone,
        'devices': devices,
        'can_change': request.user.has_perm('monitoring.change_zone'),
        'can_delete': request.user.has_perm('monitoring.delete_zone'),
    }
    
    return render(request, 'monitoring/zona_detail.html', context)


@login_required
@permission_required_with_message('monitoring.add_zone')
def zona_create(request):
    """
    Crear una nueva zona
    """
    if request.method == 'POST':
        form = ZoneForm(request.POST, request.FILES, user=request.user)
        
        if form.is_valid():
            zone = form.save(commit=False)
            
            # Si no es superusuario, asignar su organización
            if not request.user.is_superuser:
                try:
                    zone.organization = request.user.userprofile.organization
                except:
                    messages.error(request, 'Error: Usuario sin organización asignada')
                    return redirect('zona_list')
            
            zone.save()
            
            messages.success(
                request,
                f'✅ Zona "{zone.name}" creada exitosamente.'
            )
            return redirect('zona_detail', pk=zone.pk)
        else:
            messages.error(
                request,
                'Por favor corrige los errores en el formulario.'
            )
    else:
        form = ZoneForm(user=request.user)
    
    context = {
        'form': form,
        'title': 'Nueva Zona',
        'button_text': 'Crear Zona'
    }
    
    return render(request, 'monitoring/zona_form.html', context)


@login_required
@permission_required_with_message('monitoring.change_zone')
def zona_update(request, pk):
    """
    Editar una zona existente
    """
    organization = get_user_organization(request.user)
    
    # Obtener la zona
    if organization:
        zone = get_object_or_404(Zone, pk=pk, organization=organization, state='ACTIVE')
    else:
        zone = get_object_or_404(Zone, pk=pk, state='ACTIVE')
    
    if request.method == 'POST':
        form = ZoneForm(request.POST, request.FILES, instance=zone, user=request.user)
        
        if form.is_valid():
            zone = form.save()
            
            messages.success(
                request,
                f'✅ Zona "{zone.name}" actualizada exitosamente.'
            )
            return redirect('zona_detail', pk=zone.pk)
        else:
            messages.error(
                request,
                'Por favor corrige los errores en el formulario.'
            )
    else:
        form = ZoneForm(instance=zone, user=request.user)
    
    context = {
        'form': form,
        'zone': zone,
        'title': f'Editar Zona: {zone.name}',
        'button_text': 'Guardar Cambios'
    }
    
    return render(request, 'monitoring/zona_form.html', context)


@login_required
@require_POST
@ajax_permission_required('monitoring.delete_zone')
def zona_delete_ajax(request, pk):
    """
    Elimina una zona vía AJAX y responde JSON
    Compatible con SweetAlert2
    """
    # Verificar que sea AJAX
    if not request.headers.get("x-requested-with") == "XMLHttpRequest":
        return HttpResponseBadRequest("Solo peticiones AJAX")
    
    organization = get_user_organization(request.user)
    
    # Obtener la zona
    if organization:
        zone = get_object_or_404(Zone, pk=pk, organization=organization, state='ACTIVE')
    else:
        zone = get_object_or_404(Zone, pk=pk, state='ACTIVE')
    
    # Verificar si tiene dispositivos
    device_count = Device.objects.filter(zone=zone, state='ACTIVE').count()
    
    if device_count > 0:
        return JsonResponse({
            'ok': False,
            'message': f'No se puede eliminar "{zone.name}" porque tiene {device_count} dispositivo(s) asociado(s).'
        })
    
    # Soft delete
    nombre = zone.name
    zone.state = 'INACTIVE'
    zone.save()
    
    # O hard delete si prefieres:
    # zone.delete()
    
    return JsonResponse({
        'ok': True,
        'message': f'Zona "{nombre}" eliminada correctamente.'
    })


# =========================================================================
# VISTA ADICIONAL: Ejemplo de uso de sesión para filtros
# =========================================================================

@login_required
def zona_list_with_filters(request):
    """
    Lista de zonas con filtros guardados en sesión
    Ejemplo de uso avanzado de sesión
    """
    organization = get_user_organization(request.user)
    
    # Obtener filtros de la sesión
    filtros = request.session.get('filtros_zonas', {})
    
    # Aplicar nuevo filtro si viene en GET
    if request.GET.get('clear_filters'):
        # Limpiar filtros
        request.session.pop('filtros_zonas', None)
        return redirect('zona_list_with_filters')
    
    if request.GET.get('search'):
        filtros['search'] = request.GET.get('search')
        request.session['filtros_zonas'] = filtros
    
    # Base queryset
    if not organization:
        zones = Zone.objects.filter(state='ACTIVE')
    else:
        zones = Zone.objects.filter(organization=organization, state='ACTIVE')
    
    # Aplicar búsqueda si existe
    if filtros.get('search'):
        zones = zones.filter(name__icontains=filtros['search'])
    
    zones = zones.select_related('organization').order_by('name')
    
    context = {
        'zones': zones,
        'filtros': filtros,
        'can_add': request.user.has_perm('monitoring.add_zone'),
        'can_change': request.user.has_perm('monitoring.change_zone'),
        'can_delete': request.user.has_perm('monitoring.delete_zone'),
    }
    
    return render(request, 'monitoring/zona_list.html', context)


# =========================================================================
# VISTA DE LOGOUT CON LIMPIEZA DE SESIÓN
# =========================================================================

from django.contrib.auth import logout

def custom_logout(request):
    """
    Logout con limpieza de datos de sesión
    """
    # Limpiar datos específicos de la sesión
    for key in ('visitas_zonas', 'filtros_zonas', 'carrito_temp'):
        request.session.pop(key, None)
    
    # Cerrar sesión
    logout(request)
    
    # Mensaje después de logout (se crea nueva sesión vacía)
    messages.info(request, 'Sesión cerrada y datos temporales limpiados.')
    
    return redirect('login')