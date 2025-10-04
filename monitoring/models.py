# monitoring/models.py
from django.db import models
from django.contrib.auth.models import User

# Estados que pueden tener nuestros registros
STATES = [
    ('ACTIVE', 'Active'),
    ('INACTIVE', 'Inactive'),
]

# Niveles de severidad para las alertas
ALERT_SEVERITIES = [
    ('LOW', 'Low'),
    ('MEDIUM', 'Medium'), 
    ('HIGH', 'High'),
    ('CRITICAL', 'Critical'),
]

class BaseModel(models.Model):
    """
    Modelo base que contiene campos comunes para todas las tablas.
    Todos los otros modelos heredarán de este.
    """
    state = models.CharField(
        max_length=10, 
        choices=STATES, 
        default='ACTIVE',
        help_text="Estado del registro"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Fecha de creación"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Fecha de última modificación"
    )
    deleted_at = models.DateTimeField(
        null=True, 
        blank=True,
        help_text="Fecha de eliminación (soft delete)"
    )
    
    class Meta:
        abstract = True  # Esta clase no creará tabla, solo sirve de plantilla

class Organization(BaseModel):
    name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    logo = models.ImageField(upload_to='organizaciones/', null=True, blank=True)  # ← Esta línea
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Organization"
        verbose_name_plural = "Organizations"

class Category(BaseModel):
    """
    Categorías de dispositivos (ej: Sensores, Aires Acondicionados, etc.)
    """
    name = models.CharField(max_length=100, help_text="Nombre de la categoría")
    description = models.TextField(blank=True, help_text="Descripción de la categoría")
    organization = models.ForeignKey(
        Organization, 
        on_delete=models.CASCADE,
        help_text="Empresa propietaria"
    )
    icon = models.ImageField(
        upload_to='categorias/',
        null=True,
        blank=True,
        help_text="Icono de la categoría"
    )
    
    def __str__(self):
        return f"{self.name} ({self.organization.name})"
    
    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"

class Zone(BaseModel):
    """
    Zonas donde se ubican los dispositivos (ej: Oficina 1, Sala de reuniones, etc.)
    """
    name = models.CharField(max_length=100, help_text="Nombre de la zona")
    description = models.TextField(blank=True, help_text="Descripción de la zona")
    organization = models.ForeignKey(
        Organization, 
        on_delete=models.CASCADE,
        help_text="Empresa propietaria"
    )
    floor_plan = models.ImageField(
        upload_to='zonas/',
        null=True,
        blank=True,
        help_text="Plano de la zona"
    )
    
    def __str__(self):
        return f"{self.name} ({self.organization.name})"
    
    class Meta:
        verbose_name = "Zone"
        verbose_name_plural = "Zones"

class Device(BaseModel):
    """
    Dispositivos eléctricos que se monitorean
    """
    name = models.CharField(max_length=200, help_text="Nombre del dispositivo")
    description = models.TextField(blank=True, help_text="Descripción del dispositivo")
    max_consumption = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        help_text="Consumo máximo permitido (kW)"
    )
    category = models.ForeignKey(
        Category, 
        on_delete=models.CASCADE,
        help_text="Categoría del dispositivo"
    )
    zone = models.ForeignKey(
        Zone, 
        on_delete=models.CASCADE,
        help_text="Zona donde está ubicado"
    )
    organization = models.ForeignKey(
        Organization, 
        on_delete=models.CASCADE,
        help_text="Empresa propietaria"
    )
    imagen = models.ImageField(
        upload_to='dispositivos/',
        null=True,
        blank=True,
        help_text="Imagen del dispositivo"
    )
    
    def __str__(self):
        return f"{self.name} - {self.category.name}"
    
    class Meta:
        verbose_name = "Device"
        verbose_name_plural = "Devices"

class Measurement(BaseModel):
    """
    Mediciones de consumo de los dispositivos
    """
    device = models.ForeignKey(
        Device, 
        on_delete=models.CASCADE,
        help_text="Dispositivo medido"
    )
    consumption_value = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        help_text="Valor de consumo medido (kW)"
    )
    measurement_date = models.DateTimeField(
        help_text="Fecha y hora de la medición"
    )
    notes = models.TextField(blank=True, help_text="Notas adicionales")
    organization = models.ForeignKey(
        Organization, 
        on_delete=models.CASCADE,
        help_text="Empresa propietaria"
    )
    
    def __str__(self):
        return f"{self.device.name}: {self.consumption_value}kW - {self.measurement_date}"
    
    class Meta:
        verbose_name = "Measurement"
        verbose_name_plural = "Measurements"
        ordering = ['-measurement_date']  # Ordenar por fecha descendente

class Alert(BaseModel):
    """
    Alertas generadas cuando un dispositivo supera el consumo permitido
    """
    device = models.ForeignKey(
        Device, 
        on_delete=models.CASCADE,
        help_text="Dispositivo que generó la alerta"
    )
    measurement = models.ForeignKey(
        Measurement, 
        on_delete=models.CASCADE,
        help_text="Medición que generó la alerta"
    )
    severity = models.CharField(
        max_length=10, 
        choices=ALERT_SEVERITIES,
        help_text="Nivel de severidad"
    )
    message = models.TextField(help_text="Mensaje descriptivo de la alerta")
    is_resolved = models.BooleanField(
        default=False,
        help_text="¿La alerta fue resuelta?"
    )
    organization = models.ForeignKey(
        Organization, 
        on_delete=models.CASCADE,
        help_text="Empresa propietaria"
    )
    
    def __str__(self):
        return f"Alerta {self.severity}: {self.device.name} - {self.message[:50]}"
    
    class Meta:
        verbose_name = "Alert"
        verbose_name_plural = "Alerts"
        ordering = ['-created_at']