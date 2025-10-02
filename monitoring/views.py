# monitoring/views.py
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from datetime import datetime, timedelta
from .models import Organization, Device, Measurement, Alert, Category
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin

def get_user_organization(user):
    """
    Helper function para obtener la organización del usuario logueado
    """
    if hasattr(user, 'userprofile'):
        return user.userprofile.organization
    return None

@login_required
def dashboard(request):
    """
    Vista del dashboard principal
    Muestra resúmenes y datos clave para el usuario
    """
    organization = get_user_organization(request.user)
    
    if not organization:
        # Si el usuario no tiene organización, mostrar mensaje
        context = {'error': 'Usuario sin organización asignada'}
        return render(request, 'monitoring/dashboard.html', context)
    
    # Obtener últimas 10 mediciones
    latest_measurements = Measurement.objects.filter(
        organization=organization,
        state='ACTIVE'
    ).select_related('device').order_by('-measurement_date')[:10]
    
    # Contar dispositivos por zona
    devices_by_zone = Device.objects.filter(
        organization=organization,
        state='ACTIVE'
    ).values('zone__name').annotate(count=Count('id')).order_by('zone__name')
    
    # Contar dispositivos por categoría
    devices_by_category = Device.objects.filter(
        organization=organization,
        state='ACTIVE'
    ).values('category__name').annotate(count=Count('id')).order_by('category__name')
    
    # Alertas de la semana
    week_ago = datetime.now() - timedelta(days=7)
    weekly_alerts = Alert.objects.filter(
        organization=organization,
        created_at__gte=week_ago,
        state='ACTIVE'
    ).values('severity').annotate(count=Count('id'))
    
    # Convertir a diccionario para fácil acceso en template
    alerts_summary = {
        'CRITICAL': 0,
        'HIGH': 0,
        'MEDIUM': 0,
        'LOW': 0
    }
    for alert in weekly_alerts:
        alerts_summary[alert['severity']] = alert['count']
    
    # Alertas recientes (últimas 5)
    recent_alerts = Alert.objects.filter(
        organization=organization,
        state='ACTIVE'
    ).select_related('device').order_by('-created_at')[:5]
    
    context = {
        'organization': organization,
        'latest_measurements': latest_measurements,
        'devices_by_zone': devices_by_zone,
        'devices_by_category': devices_by_category,
        'alerts_summary': alerts_summary,
        'recent_alerts': recent_alerts,
    }
    
    return render(request, 'monitoring/dashboard.html', context)

@login_required
def device_list(request):
    """
    Vista para listar dispositivos con filtro por categoría
    """
    organization = get_user_organization(request.user)
    
    if not organization:
        context = {'error': 'Usuario sin organización asignada'}
        return render(request, 'monitoring/device_list.html', context)
    
    # Obtener todas las categorías para el filtro
    categories = Category.objects.filter(
        organization=organization,
        state='ACTIVE'
    ).order_by('name')
    
    # Obtener dispositivos
    devices = Device.objects.filter(
        organization=organization,
        state='ACTIVE'
    ).select_related('category', 'zone')
    
    # Aplicar filtro por categoría si se seleccionó
    selected_category = request.GET.get('category')
    selected_category_name = None
    
    if selected_category:
        devices = devices.filter(category_id=selected_category)
        # Obtener el nombre de la categoría seleccionada
        try:
            selected_category_obj = categories.get(id=selected_category)
            selected_category_name = selected_category_obj.name
        except Category.DoesNotExist:
            pass
    
    devices = devices.order_by('name')
    
    context = {
        'devices': devices,
        'categories': categories,
        'selected_category': selected_category,
        'selected_category_name': selected_category_name,
        'organization': organization,
    }
    
    return render(request, 'monitoring/device_list.html', context)

@login_required
def device_detail(request, device_id):
    """
    Vista para mostrar el detalle de un dispositivo específico
    """
    organization = get_user_organization(request.user)
    
    device = get_object_or_404(
        Device, 
        id=device_id, 
        organization=organization,
        state='ACTIVE'
    )
    
    # Obtener mediciones del dispositivo (últimas 20)
    measurements = Measurement.objects.filter(
        device=device,
        state='ACTIVE'
    ).order_by('-measurement_date')[:20]
    
    # Obtener alertas del dispositivo (últimas 10)
    alerts = Alert.objects.filter(
        device=device,
        state='ACTIVE'
    ).order_by('-created_at')[:10]
    
    context = {
        'device': device,
        'measurements': measurements,
        'alerts': alerts,
        'organization': organization,
    }
    
    return render(request, 'monitoring/device_detail.html', context)

@login_required
def measurement_list(request):
    """
    Vista para listar todas las mediciones
    """
    organization = get_user_organization(request.user)
    
    if not organization:
        context = {'error': 'Usuario sin organización asignada'}
        return render(request, 'monitoring/measurement_list.html', context)
    
    # Obtener mediciones (últimas 50)
    measurements = Measurement.objects.filter(
        organization=organization,
        state='ACTIVE'
    ).select_related('device').order_by('-measurement_date')[:50]
    
    context = {
        'measurements': measurements,
        'organization': organization,
    }
    
    return render(request, 'monitoring/measurement_list.html', context)