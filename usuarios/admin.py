from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import UserProfile

# =========================================================================
# PERFIL DE USUARIO (UserProfile)
# =========================================================================

class UserProfileInline(admin.StackedInline):
    """
    Inline para editar UserProfile directamente desde el User
    """
    model = UserProfile
    can_delete = False
    verbose_name = 'Perfil de Usuario'
    verbose_name_plural = 'Perfiles de Usuario'
    extra = 0
    
    fieldsets = (
        ('Información de la Organización', {
            'fields': ('organization', 'position', 'phone')
        }),
    )

class UserAdmin(BaseUserAdmin):
    """
    Admin personalizado para User que incluye UserProfile inline
    """
    inlines = (UserProfileInline,)
    
    # Agregar organización en la lista de usuarios
    list_display = (
        'username',
        'email',
        'first_name',
        'last_name',
        'get_organization',
        'is_staff',
        'is_active'
    )
    
    list_filter = (
        'is_staff',
        'is_superuser',
        'is_active',
        'groups',
        'userprofile__organization'  # Filtrar por organización
    )
    
    search_fields = (
        'username',
        'first_name',
        'last_name',
        'email',
        'userprofile__organization__name'
    )
    
    def get_organization(self, obj):
        """Mostrar organización del usuario"""
        try:
            return obj.userprofile.organization.name
        except:
            return '-'
    get_organization.short_description = 'Organización'
    get_organization.admin_order_field = 'userprofile__organization__name'

# Desregistrar el User admin por defecto y registrar el personalizado
try:
    admin.site.unregister(User)
except admin.sites.NotRegistered:
    pass

admin.site.register(User, UserAdmin)

# =========================================================================
# REGISTRO DIRECTO DE USERPROFILE (opcional)
# =========================================================================

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """
    Admin para ver perfiles directamente (además del inline)
    """
    list_display = (
        'user',
        'organization',
        'position',
        'phone',
        'created_at'
    )
    
    search_fields = (
        'user__username',
        'user__first_name',
        'user__last_name',
        'organization__name',
        'position'
    )
    
    list_filter = (
        'organization',
        'created_at'
    )
    
    ordering = ('organization', 'user__username')
    
    list_select_related = ('user', 'organization')
    
    list_per_page = 50
    
    readonly_fields = ('created_at',)
    
    fieldsets = (
        ('Usuario', {
            'fields': ('user',)
        }),
        ('Información Laboral', {
            'fields': ('organization', 'position', 'phone')
        }),
        ('Metadatos', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )