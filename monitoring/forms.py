"""
Formularios personalizados con validaciones para Django Admin
"""
from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import Device, Measurement, Alert, Organization

class DeviceAdminForm(forms.ModelForm):
    """
    Formulario personalizado para Device con validaciones
    """
    class Meta:
        model = Device
        fields = '__all__'
    
    def clean_max_consumption(self):
        """
        Validar que el consumo máximo sea positivo y razonable
        """
        max_consumption = self.cleaned_data.get('max_consumption')
        
        if max_consumption and max_consumption <= 0:
            raise ValidationError(
                'El consumo máximo debe ser mayor a 0 kW.'
            )
        
        if max_consumption and max_consumption > 1000:
            raise ValidationError(
                'El consumo máximo parece muy alto (>1000 kW). '
                'Verifica que el valor sea correcto.'
            )
        
        return max_consumption
    
    def clean_name(self):
        """
        Validar que el nombre no esté duplicado en la misma organización
        """
        name = self.cleaned_data.get('name')
        organization = self.cleaned_data.get('organization')
        
        if name and organization:
            # Excluir el objeto actual si estamos editando
            qs = Device.objects.filter(
                name=name,
                organization=organization
            )
            
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            
            if qs.exists():
                raise ValidationError(
                    f'Ya existe un dispositivo con el nombre "{name}" '
                    f'en la organización {organization.name}.'
                )
        
        return name
    
    def clean(self):
        """
        Validaciones que involucran múltiples campos
        """
        cleaned_data = super().clean()
        zone = cleaned_data.get('zone')
        organization = cleaned_data.get('organization')
        
        # Verificar que la zona pertenezca a la organización
        if zone and organization:
            if zone.organization != organization:
                raise ValidationError(
                    f'La zona "{zone.name}" no pertenece a la organización '
                    f'"{organization.name}". Selecciona una zona válida.'
                )
        
        return cleaned_data

class MeasurementAdminForm(forms.ModelForm):
    """
    Formulario personalizado para Measurement con validaciones
    """
    class Meta:
        model = Measurement
        fields = '__all__'
    
    def clean_consumption_value(self):
        """
        Validar que el valor de consumo sea positivo
        """
        consumption_value = self.cleaned_data.get('consumption_value')
        
        if consumption_value and consumption_value < 0:
            raise ValidationError(
                'El valor de consumo no puede ser negativo.'
            )
        
        if consumption_value and consumption_value == 0:
            raise ValidationError(
                'El valor de consumo debe ser mayor a 0 kW. '
                'Si el dispositivo está apagado, considera no registrar la medición.'
            )
        
        return consumption_value
    
    def clean_measurement_date(self):
        """
        Validar que la fecha de medición no sea futura
        """
        measurement_date = self.cleaned_data.get('measurement_date')
        
        if measurement_date and measurement_date > timezone.now():
            raise ValidationError(
                'La fecha de medición no puede ser futura. '
                'Verifica la fecha ingresada.'
            )
        
        return measurement_date
    
    def clean(self):
        """
        Validación: generar alerta si el consumo excede el límite
        """
        cleaned_data = super().clean()
        device = cleaned_data.get('device')
        consumption_value = cleaned_data.get('consumption_value')
        
        if device and consumption_value:
            if consumption_value > device.max_consumption:
                # Agregar advertencia (no error, solo información)
                self.add_error(None, ValidationError(
                    f'⚠️ ADVERTENCIA: El consumo ({consumption_value} kW) excede '
                    f'el límite del dispositivo ({device.max_consumption} kW). '
                    f'Se recomienda generar una alerta.',
                    code='exceeds_limit'
                ))
        
        return cleaned_data

class AlertAdminForm(forms.ModelForm):
    """
    Formulario personalizado para Alert con validaciones
    """
    class Meta:
        model = Alert
        fields = '__all__'
    
    def clean(self):
        """
        Validar que la medición corresponda al mismo dispositivo
        """
        cleaned_data = super().clean()
        device = cleaned_data.get('device')
        measurement = cleaned_data.get('measurement')
        
        if device and measurement:
            if measurement.device != device:
                raise ValidationError(
                    f'La medición seleccionada pertenece a "{measurement.device.name}", '
                    f'no a "{device.name}". Selecciona una medición del dispositivo correcto.'
                )
        
        return cleaned_data

class OrganizationAdminForm(forms.ModelForm):
    """
    Formulario personalizado para Organization con validaciones
    """
    class Meta:
        model = Organization
        fields = '__all__'
    
    def clean_name(self):
        """
        Validar longitud del nombre
        """
        name = self.cleaned_data.get('name')
        
        if name and len(name) < 3:
            raise ValidationError(
                'El nombre debe tener al menos 3 caracteres.'
            )
        
        if name and len(name) > 200:
            raise ValidationError(
                'El nombre no puede exceder 200 caracteres.'
            )
        
        return name
    
    def clean_email(self):
        """
        Validar que el email sea único
        """
        email = self.cleaned_data.get('email')
        
        if email:
            qs = Organization.objects.filter(email=email)
            
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            
            if qs.exists():
                raise ValidationError(
                    f'Ya existe una organización con el email "{email}". '
                    'Los emails deben ser únicos.'
                )
        
        return email
    
    def clean_phone(self):
        """
        Validar formato de teléfono (básico)
        """
        phone = self.cleaned_data.get('phone')
        
        if phone:
            # Remover espacios y caracteres comunes
            phone_clean = phone.replace(' ', '').replace('-', '').replace('+', '')
            
            if not phone_clean.isdigit():
                raise ValidationError(
                    'El teléfono debe contener solo números, espacios, guiones o el símbolo +.'
                )
            
            if len(phone_clean) < 7:
                raise ValidationError(
                    'El teléfono debe tener al menos 7 dígitos.'
                )
        
        return phone

# =========================================================================
# INLINE FORMSETS CON VALIDACIONES
# =========================================================================

from django.forms import BaseInlineFormSet

class ZoneInlineFormSet(BaseInlineFormSet):
    """
    Formset personalizado para validar Zones en Organization
    """
    def clean(self):
        """
        Validar que no haya nombres de zonas duplicados en la misma organización
        """
        super().clean()
        
        if any(self.errors):
            return
        
        names = []
        for form in self.forms:
            if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                name = form.cleaned_data.get('name')
                if name:
                    if name in names:
                        raise ValidationError(
                            f'No puedes tener dos zonas con el mismo nombre "{name}" '
                            'en la misma organización.'
                        )
                    names.append(name)

class DeviceInlineFormSet(BaseInlineFormSet):
    """
    Formset personalizado para validar Devices en Zone
    """
    def clean(self):
        """
        Validar que haya al menos 1 dispositivo activo por zona
        """
        super().clean()
        
        if any(self.errors):
            return
        
        active_count = 0
        for form in self.forms:
            if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                if form.cleaned_data.get('state') == 'ACTIVE':
                    active_count += 1
        
        # Advertencia, no error crítico
        if active_count == 0:
            # Solo advertencia en consola, no bloquea el guardado
            import warnings
            warnings.warn('No hay dispositivos activos en esta zona.')