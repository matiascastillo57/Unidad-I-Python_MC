from django.db import models
from django.contrib.auth.models import User, Group
from django.conf import settings
from monitoring.models import Organization

class UserProfile(models.Model):
    """
    Perfil de usuario que extiende el modelo User de Django
    y lo relaciona con una organización
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        help_text="Usuario de Django"
    )
    organization = models.ForeignKey(
        Organization,
        on_delete=models.PROTECT,  # No permitir eliminar org si tiene usuarios
        help_text="Empresa a la que pertenece el usuario"
    )
    
    # Campos adicionales
    rut = models.CharField(
        max_length=12,
        unique=True,
        blank=True,
        null=True,
        help_text="RUT del usuario (sin puntos, con guión)"
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        help_text="Teléfono del usuario"
    )
    position = models.CharField(
        max_length=100,
        blank=True,
        help_text="Cargo en la empresa"
    )
    direccion = models.TextField(
        blank=True,
        help_text="Dirección del usuario"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} @ {self.organization.name}"
    
    def get_role(self):
        """Obtener el rol principal del usuario"""
        groups = self.user.groups.all()
        if groups.exists():
            return groups.first().name
        return "Sin rol"
    
    class Meta:
        verbose_name = "Perfil de Usuario"
        verbose_name_plural = "Perfiles de Usuario"


class Module(models.Model):
    """
    Módulos del sistema (ej: Ventas, RRHH, Inventario)
    """
    code = models.SlugField(
        max_length=50,
        unique=True,
        help_text="Código único del módulo (ej: ventas, rrhh)"
    )
    name = models.CharField(
        max_length=100,
        help_text="Nombre visible del módulo"
    )
    description = models.TextField(
        blank=True,
        help_text="Descripción del módulo"
    )
    icon = models.CharField(
        max_length=50,
        blank=True,
        help_text="Clase de icono CSS (ej: bi-cart para Bootstrap Icons)"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="¿El módulo está activo?"
    )
    order = models.IntegerField(
        default=0,
        help_text="Orden de visualización en menús"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Módulo"
        verbose_name_plural = "Módulos"
        ordering = ['order', 'name']


class Role(models.Model):
    """
    Roles del sistema (1:1 con Groups de Django)
    """
    group = models.OneToOneField(
        Group,
        on_delete=models.CASCADE,
        related_name="role",
        help_text="Grupo de Django asociado"
    )
    description = models.TextField(
        blank=True,
        help_text="Descripción del rol"
    )
    is_client_role = models.BooleanField(
        default=True,
        help_text="¿Es un rol de cliente? (False = rol interno de EcoEnergy)"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.group.name
    
    class Meta:
        verbose_name = "Rol"
        verbose_name_plural = "Roles"


class RoleModulePermission(models.Model):
    """
    Permisos de un rol sobre un módulo específico
    """
    role = models.ForeignKey(
        Role,
        on_delete=models.CASCADE,
        related_name="module_perms",
        help_text="Rol"
    )
    module = models.ForeignKey(
        Module,
        on_delete=models.CASCADE,
        related_name="role_perms",
        help_text="Módulo"
    )
    
    # Permisos CRUD
    can_view = models.BooleanField(
        default=False,
        help_text="Puede ver/listar"
    )
    can_add = models.BooleanField(
        default=False,
        help_text="Puede agregar"
    )
    can_change = models.BooleanField(
        default=False,
        help_text="Puede modificar"
    )
    can_delete = models.BooleanField(
        default=False,
        help_text="Puede eliminar"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ("role", "module")
        verbose_name = "Permiso Rol-Módulo"
        verbose_name_plural = "Permisos Rol-Módulo"
    
    def __str__(self):
        perms = []
        if self.can_view: perms.append('Ver')
        if self.can_add: perms.append('Agregar')
        if self.can_change: perms.append('Cambiar')
        if self.can_delete: perms.append('Eliminar')
        perms_str = ', '.join(perms) if perms else 'Sin permisos'
        return f"{self.role} → {self.module} ({perms_str})"