#usuarios/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import UserProfile, Module, Role, RoleModulePermission

# =========================================================================
# USER PROFILE
# =========================================================================

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name = 'Perfil de Usuario'
    verbose_name_plural = 'Perfiles de Usuario'
    extra = 0
    
    fieldsets = (
        ('Información de la Organización', {
            'fields': ('organization', 'position')
        }),
        ('Datos Personales', {
            'fields': ('rut', 'phone', 'direccion')
        }),
    )

class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    
    list_display = (
        'username',
        'email',
        'first_name',
        'last_name',
        'get_organization',
        'get_role',
        'is_staff',
        'is_active'
    )
    
    list_filter = (
        'is_staff',
        'is_superuser',
        'is_active',
        'groups',
        'userprofile__organization'
    )
    
    search_fields = (
        'username',
        'first_name',
        'last_name',
        'email',
        'userprofile__organization__name',
        'userprofile__rut'
    )
    
    def get_organization(self, obj):
        try:
            return obj.userprofile.organization.name
        except:
            return '-'
    get_organization.short_description = 'Organización'
    get_organization.admin_order_field = 'userprofile__organization__name'
    
    def get_role(self, obj):
        try:
            return obj.userprofile.get_role()
        except:
            return '-'
    get_role.short_description = 'Rol'

try:
    admin.site.unregister(User)
except admin.sites.NotRegistered:
    pass

admin.site.register(User, UserAdmin)

# =========================================================================
# USER PROFILE DIRECTO
# =========================================================================

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'organization',
        'position',
        'rut',
        'phone',
        'get_role',
        'created_at'
    )
    
    search_fields = (
        'user__username',
        'user__first_name',
        'user__last_name',
        'organization__name',
        'position',
        'rut'
    )
    
    list_filter = (
        'organization',
        'created_at',
        'user__groups'
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
            'fields': ('organization', 'position')
        }),
        ('Datos Personales', {
            'fields': ('rut', 'phone', 'direccion')
        }),
        ('Metadatos', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def get_role(self, obj):
        return obj.get_role()
    get_role.short_description = 'Rol'

# =========================================================================
# MÓDULOS
# =========================================================================

@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'code',
        'icon',
        'order',
        'is_active',
        'created_at'
    )
    
    search_fields = ('name', 'code', 'description')
    list_filter = ('is_active', 'created_at')
    ordering = ('order', 'name')
    list_per_page = 50
    readonly_fields = ('created_at',)
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('code', 'name', 'description')
        }),
        ('Visualización', {
            'fields': ('icon', 'order', 'is_active')
        }),
        ('Metadatos', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

# =========================================================================
# PERMISOS ROL-MÓDULO (INLINE)
# =========================================================================

class RoleModulePermissionInline(admin.TabularInline):
    model = RoleModulePermission
    extra = 0
    fields = ('module', 'can_view', 'can_add', 'can_change', 'can_delete')
    verbose_name = 'Permiso de Módulo'
    verbose_name_plural = 'Permisos de Módulos'

# =========================================================================
# ROLES
# =========================================================================

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = (
        'get_role_name',
        'description_short',
        'is_client_role',
        'user_count',
        'module_count',
        'created_at'
    )
    
    search_fields = ('group__name', 'description')
    list_filter = ('is_client_role', 'created_at')
    ordering = ('group__name',)
    list_per_page = 50
    readonly_fields = ('created_at', 'user_count', 'module_count')
    
    inlines = [RoleModulePermissionInline]
    
    fieldsets = (
        ('Grupo Django', {
            'fields': ('group',)
        }),
        ('Información del Rol', {
            'fields': ('description', 'is_client_role')
        }),
        ('Estadísticas', {
            'fields': ('user_count', 'module_count', 'created_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_role_name(self, obj):
        return obj.group.name
    get_role_name.short_description = 'Rol'
    get_role_name.admin_order_field = 'group__name'
    
    def description_short(self, obj):
        if obj.description and len(obj.description) > 50:
            return obj.description[:50] + '...'
        return obj.description or '-'
    description_short.short_description = 'Descripción'
    
    def user_count(self, obj):
        count = obj.group.user_set.count()
        return f'{count} usuario(s)'
    user_count.short_description = 'Usuarios'
    
    def module_count(self, obj):
        count = obj.module_perms.count()
        return f'{count} módulo(s)'
    module_count.short_description = 'Módulos Asignados'

# =========================================================================
# PERMISOS ROL-MÓDULO (DIRECTO)
# =========================================================================

@admin.register(RoleModulePermission)
class RoleModulePermissionAdmin(admin.ModelAdmin):
    list_display = (
        'role',
        'module',
        'permissions_display',
        'created_at'
    )
    
    search_fields = (
        'role__group__name',
        'module__name',
        'module__code'
    )
    
    list_filter = (
        'role',
        'module',
        'can_view',
        'can_add',
        'can_change',
        'can_delete'
    )
    
    ordering = ('role__group__name', 'module__name')
    list_select_related = ('role', 'role__group', 'module')
    list_per_page = 50
    readonly_fields = ('created_at',)
    
    fieldsets = (
        ('Asignación', {
            'fields': ('role', 'module')
        }),
        ('Permisos CRUD', {
            'fields': (
                ('can_view', 'can_add'),
                ('can_change', 'can_delete')
            )
        }),
        ('Metadatos', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def permissions_display(self, obj):
        perms = []
        if obj.can_view:
            perms.append('✓ Ver')
        if obj.can_add:
            perms.append('✓ Agregar')
        if obj.can_change:
            perms.append('✓ Cambiar')
        if obj.can_delete:
            perms.append('✓ Eliminar')
        
        if not perms:
            return '✗ Sin permisos'
        
        return ' | '.join(perms)
    permissions_display.short_description = 'Permisos'