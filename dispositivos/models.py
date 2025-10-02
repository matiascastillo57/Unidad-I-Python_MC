from django.db import models
from django.utils import timezone

# Constantes
ESTADOS = [
    ("ACTIVO", "Activo"), 
    ("INACTIVO", "Inactivo"),
]

TIPOS_ALERTA = [
    ("CRITICO", "Crítico"),
    ("ADVERTENCIA", "Advertencia"),
    ("INFO", "Información"),
]

class BaseModel(models.Model):
    """Modelo base con campos comunes para todas las tablas"""
    estado = models.CharField(max_length=10, choices=ESTADOS, default="ACTIVO")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        abstract = True  # No crea tabla, solo herencia

class Categoria(BaseModel):
    """Clasifica los dispositivos en grupos"""
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    
    def __str__(self):
        return self.nombre
    
    class Meta:
        verbose_name_plural = "Categorías"

class Zona(BaseModel):
    """Ubicación donde está instalado el dispositivo"""
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    
    def __str__(self):
        return self.nombre

class Dispositivo(BaseModel):
    """Equipo eléctrico que se monitorea"""
    nombre = models.CharField(max_length=100)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    zona = models.ForeignKey(Zona, on_delete=models.CASCADE)
    consumo_max = models.IntegerField(help_text="Consumo máximo permitido en Watts")
    consumo_actual = models.IntegerField(default=0, help_text="Consumo actual en Watts")
    
    def __str__(self):
        return self.nombre
    
    def esta_en_limite(self):
        """Verifica si el consumo está dentro del límite"""
        return self.consumo_actual <= self.consumo_max
    
    def porcentaje_consumo(self):
        """Calcula el porcentaje de consumo actual vs máximo"""
        if self.consumo_max > 0:
            return round((self.consumo_actual / self.consumo_max) * 100, 1)
        return 0

class Medicion(BaseModel):
    """Guarda el consumo de un dispositivo en un momento específico"""
    dispositivo = models.ForeignKey(Dispositivo, on_delete=models.CASCADE, related_name='mediciones')
    consumo = models.IntegerField(help_text="Consumo medido en Watts")
    fecha_medicion = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"{self.dispositivo.nombre} - {self.consumo}W - {self.fecha_medicion.strftime('%d/%m/%Y %H:%M')}"
    
    class Meta:
        verbose_name_plural = "Mediciones"
        ordering = ['-fecha_medicion']

class Alerta(BaseModel):
    """Notificación cuando un dispositivo excede el consumo permitido"""
    dispositivo = models.ForeignKey(Dispositivo, on_delete=models.CASCADE, related_name='alertas')
    tipo = models.CharField(max_length=15, choices=TIPOS_ALERTA, default="ADVERTENCIA")
    mensaje = models.TextField()
    fecha_alerta = models.DateTimeField(default=timezone.now)
    resuelta = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.tipo} - {self.dispositivo.nombre}"
    
    class Meta:
        ordering = ['-fecha_alerta']