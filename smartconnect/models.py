from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinLengthValidator

class Departamento(models.Model):
    """Representa zonas o áreas físicas"""
    nombre = models.CharField(
        max_length=100, 
        validators=[MinLengthValidator(3)],
        unique=True
    )
    descripcion = models.TextField(blank=True)
    ubicacion = models.CharField(max_length=200, blank=True)
    activo = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Departamento"
        verbose_name_plural = "Departamentos"
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Sensor(models.Model):
    """Sensores RFID (tarjetas o llaveros)"""
    
    ESTADO_CHOICES = [
        ('activo', 'Activo'),
        ('inactivo', 'Inactivo'),
        ('bloqueado', 'Bloqueado'),
        ('perdido', 'Perdido'),
    ]
    
    uid_mac = models.CharField(
        max_length=50, 
        unique=True,
        verbose_name="UID/MAC",
        help_text="Código único del sensor RFID"
    )
    nombre = models.CharField(
        max_length=100,
        validators=[MinLengthValidator(3)]
    )
    estado = models.CharField(
        max_length=20, 
        choices=ESTADO_CHOICES, 
        default='activo'
    )
    departamento = models.ForeignKey(
        Departamento, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='sensores'
    )
    usuario_asignado = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='sensores'
    )
    descripcion = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Sensor"
        verbose_name_plural = "Sensores"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.nombre} ({self.uid_mac})"


class Barrera(models.Model):
    """Control de barrera de acceso"""
    
    ESTADO_CHOICES = [
        ('abierta', 'Abierta'),
        ('cerrada', 'Cerrada'),
    ]
    
    nombre = models.CharField(max_length=100, unique=True)
    estado = models.CharField(
        max_length=20, 
        choices=ESTADO_CHOICES, 
        default='cerrada'
    )
    departamento = models.ForeignKey(
        Departamento,
        on_delete=models.CASCADE,
        related_name='barreras'
    )
    ultima_accion = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Barrera"
        verbose_name_plural = "Barreras"

    def __str__(self):
        return f"{self.nombre} - {self.estado}"

    def abrir(self):
        self.estado = 'abierta'
        self.save()

    def cerrar(self):
        self.estado = 'cerrada'
        self.save()


class Evento(models.Model):
    """Registro de eventos de acceso"""
    
    TIPO_CHOICES = [
        ('acceso_permitido', 'Acceso Permitido'),
        ('acceso_denegado', 'Acceso Denegado'),
        ('apertura_manual', 'Apertura Manual'),
        ('cierre_manual', 'Cierre Manual'),
    ]
    
    sensor = models.ForeignKey(
        Sensor,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='eventos'
    )
    barrera = models.ForeignKey(
        Barrera,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='eventos'
    )
    tipo = models.CharField(max_length=30, choices=TIPO_CHOICES)
    usuario_responsable = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Usuario que generó el evento manual"
    )
    descripcion = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_origen = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        verbose_name = "Evento"
        verbose_name_plural = "Eventos"
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.tipo} - {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"


class PerfilUsuario(models.Model):
    """Extensión del modelo User para roles"""
    
    ROL_CHOICES = [
        ('admin', 'Administrador'),
        ('operador', 'Operador'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    rol = models.CharField(max_length=20, choices=ROL_CHOICES, default='operador')
    telefono = models.CharField(max_length=20, blank=True)
    departamento = models.ForeignKey(
        Departamento,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Perfil de Usuario"
        verbose_name_plural = "Perfiles de Usuarios"

    def __str__(self):
        return f"{self.user.username} - {self.rol}"

    def es_admin(self):
        return self.rol == 'admin'

    def es_operador(self):
        return self.rol == 'operador'