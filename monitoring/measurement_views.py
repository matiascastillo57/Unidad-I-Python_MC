# monitoring/measurement_views.py
"""
Vistas CRUD para Measurement (Mediciones)
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseBadRequest
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.db.models import Q
from django.utils import timezone
from django.core.paginator import Paginator
from django import forms

from .models import Measurement, Device, Organization, Alert
from ecoenergy.decorators import permission_required_with_message, ajax_permission_required


class MeasurementForm(forms.ModelForm):
    class Meta:
        model = Measurement
        fields = ['device', 'consumption_value', 'measurement_date', 'notes', 'organization']
        widgets = {
            'device': forms.Select(attrs={'class': 'form-select'}),
            'consumption_value': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'measurement_date': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'organization': forms.Select(attrs={'class': 'form-select'})
        }
        labels = {
            'device': 'Dispositivo',
            'consumption_value': 'Consumo (kW)',
            'measurement_date': 'Fecha/Hora de Medición',
            'notes': 'Notas',
            'organization': 'Organización'
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user and not user.is_superuser:
            try:
                user_org = user.userprofile.organization
                self.fields['organization'].queryset = Organization.objects.filter(id=user_org.id)
                self.fields['organization'].initial = user_org.id
                self.fields['device'].queryset = Device.objects.filter(organization=user_org, state='ACTIVE')
            except:
                self.fields['organization'].queryset = Organization.objects.none()
                self.fields['device'].queryset = Device.objects.none()
        
        # Valor inicial para fecha
        if not self.instance.pk:
            self.fields['measurement_date'].initial = timezone.now()
    
    def clean_consumption_value(self):
        value = self.cleaned_data.get('consumption_value')
        if value and value <= 0:
            raise forms.ValidationError('El consumo debe ser mayor a 0 kW.')
        if value and value > 10000:
            raise forms.ValidationError('El consumo parece demasiado alto. Verifica el valor.')
        return value
    
    def clean_measurement_date(self):
        date = self.cleaned_data.get('measurement_date')
        if date and date > timezone.now():
            raise forms.ValidationError('La fecha de medición no puede ser futura.')
        return date
    
    def clean(self):
        cleaned_data = super().clean()
        device = cleaned_data.get('device')
        consumption = cleaned_data.get('consumption_value')
        organization = cleaned_data.get('organization')
        
        if device and organization:
            if device.organization != organization:
                raise forms.ValidationError('El dispositivo no pertenece a la organización seleccionada.')
        
        return cleaned_data


def get_user_organization(user):
    if user.is_superuser:
        return None
    try:
        return user.userprofile.organization
    except:
        return None


@login_required
@permission_required_with_message('monitoring.view_measurement')
def measurement_list(request):
    """Lista de mediciones con filtros, búsqueda y paginación"""
    organization = get_user_organization(request.user)
    
    # Base queryset
    if not organization:
        measurements = Measurement.objects.filter(state='ACTIVE')
        devices = Device.objects.filter(state='ACTIVE')
    else:
        measurements = Measurement.objects.filter(organization=organization, state='ACTIVE')
        devices = Device.objects.filter(organization=organization, state='ACTIVE')
    
    # 1. FILTROS
    device_filter = request.GET.get('device')
    search = request.GET.get('q', '')  # Cambiado de 'search' a 'q' para consistencia
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    
    if device_filter:
        measurements = measurements.filter(device_id=device_filter)
    
    if search:
        measurements = measurements.filter(
            Q(device__name__icontains=search) |
            Q(notes__icontains=search)
        )
    
    if date_from:
        measurements = measurements.filter(measurement_date__gte=date_from)
    
    if date_to:
        measurements = measurements.filter(measurement_date__lte=date_to)
    
    # 2. ORDENAMIENTO
    sort = request.GET.get('sort', '-measurement_date')
    valid_sorts = ['measurement_date', '-measurement_date', 'consumption_value', '-consumption_value', 
                   'device__name', '-device__name']
    
    if sort in valid_sorts:
        measurements = measurements.order_by(sort)
    else:
        measurements = measurements.order_by('-measurement_date')
    
    # Optimizar queries
    measurements = measurements.select_related('device', 'device__zone', 'device__category')
    
    # 3. PAGINACIÓN
    per_page = request.GET.get('per_page', request.session.get('per_page', 10))
    
    try:
        per_page = int(per_page)
        if per_page in [5, 10, 25, 50]:
            request.session['per_page'] = per_page
    except (ValueError, TypeError):
        per_page = 10
    
    paginator = Paginator(measurements, per_page)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    # 4. QUERYSTRING para mantener parámetros
    querystring = request.GET.copy()
    if 'page' in querystring:
        querystring.pop('page')
    
    context = {
        'page_obj': page_obj,
        'devices': devices,
        'organization': organization,
        'device_filter': device_filter,
        'q': search,
        'sort': sort,
        'per_page': per_page,
        'date_from': date_from,
        'date_to': date_to,
        'querystring': querystring.urlencode(),
        'can_add': request.user.has_perm('monitoring.add_measurement'),
        'can_change': request.user.has_perm('monitoring.change_measurement'),
        'can_delete': request.user.has_perm('monitoring.delete_measurement'),
    }
    
    return render(request, 'monitoring/measurement_list_new.html', context)


@login_required
@permission_required_with_message('monitoring.add_measurement')
def measurement_create(request):
    """Crear nueva medición"""
    if request.method == 'POST':
        form = MeasurementForm(request.POST, user=request.user)
        
        if form.is_valid():
            measurement = form.save(commit=False)
            
            # ⬇️ AGREGAR ESTO
            measurement.state = 'ACTIVE'  # ⬅️ IMPORTANTE
            
            if not request.user.is_superuser:
                try:
                    measurement.organization = request.user.userprofile.organization
                except:
                    messages.error(request, 'Error: Usuario sin organización')
                    return redirect('measurement_list')
            
            measurement.save()
            
            # Generar alerta si excede límite
            if measurement.consumption_value > measurement.device.max_consumption:
                Alert.objects.create(
                    device=measurement.device,
                    measurement=measurement,
                    severity='HIGH',
                    message=f'Consumo excedido: {measurement.consumption_value} kW (límite: {measurement.device.max_consumption} kW)',
                    organization=measurement.organization,
                    state='ACTIVE'  # ⬅️ TAMBIÉN AQUÍ
                )
                messages.warning(request, f'⚠️ Se generó una alerta: consumo excede el límite')
            
            messages.success(request, f'✅ Medición registrada: {measurement.consumption_value} kW')
            return redirect('measurement_list')
        else:
            messages.error(request, 'Corrige los errores en el formulario.')
    else:
        form = MeasurementForm(user=request.user)
    
    return render(request, 'monitoring/measurement_form.html', {
        'form': form,
        'title': 'Nueva Medición',
        'button_text': 'Registrar Medición'
    })


@login_required
@permission_required_with_message('monitoring.change_measurement')
def measurement_update(request, pk):
    """Editar medición"""
    organization = get_user_organization(request.user)
    
    if organization:
        measurement = get_object_or_404(Measurement, pk=pk, organization=organization, state='ACTIVE')
    else:
        measurement = get_object_or_404(Measurement, pk=pk, state='ACTIVE')
    
    if request.method == 'POST':
        form = MeasurementForm(request.POST, instance=measurement, user=request.user)
        if form.is_valid():
            measurement = form.save()
            messages.success(request, '✅ Medición actualizada correctamente.')
            return redirect('measurement_list')
    else:
        form = MeasurementForm(instance=measurement, user=request.user)
    
    return render(request, 'monitoring/measurement_form.html', {
        'form': form,
        'measurement': measurement,
        'title': f'Editar Medición',
        'button_text': 'Guardar Cambios'
    })


@login_required
@require_POST
@ajax_permission_required('monitoring.delete_measurement')
def measurement_delete_ajax(request, pk):
    """Eliminar medición vía AJAX"""
    if not request.headers.get("x-requested-with") == "XMLHttpRequest":
        return HttpResponseBadRequest("Solo AJAX")
    
    organization = get_user_organization(request.user)
    
    if organization:
        measurement = get_object_or_404(Measurement, pk=pk, organization=organization, state='ACTIVE')
    else:
        measurement = get_object_or_404(Measurement, pk=pk, state='ACTIVE')
    
    # Soft delete
    measurement.state = 'INACTIVE'
    measurement.save()
    
    return JsonResponse({
        'ok': True,
        'message': f'Medición eliminada correctamente.'
    })