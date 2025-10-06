from django.contrib import admin
from django.db.models import Sum, Avg, Count
from django.utils.html import format_html
from .models import Organization, Category, Zone, Device, Measurement, Alert

# =========================================================================
# HELPER FUNCTION PARA SCOPING
# =========================================================================

def get_user_organization(user):
    """
    Obtener organización del usuario logueado
    Retorna None si no tiene organización o no es staff
    """
    if user.is_superuser:
        return None  # Superusuario ve todo
    
    try:
        return user.userprofile.organization
    except:
        return None

# =========================================================================
# PERSONALIZACIÓN DEL SITIO ADMIN
# =========================================================================
admin.site.site_header = "EcoEnergy — Admin Pro"
admin.site.site_title = "EcoEnergy Admin Pro"
admin.site.index_title = "Panel de Administración Profesional"

# =========================================================================
# ACCIONES PERSONALIZADAS (ACTIONS)
# =========================================================================

@admin.action(description="✅ Activar elementos seleccionados")
def make_active(modeladmin, request, queryset):
    updated = queryset.update(state='ACTIVE')
    modeladmin.message_user(request, f'{updated} elemento(s) activado(s) correctamente.')

@admin.action(description="❌ Desactivar elementos seleccionados")
def make_inactive(modeladmin, request, queryset):
    updated = queryset.update(state='INACTIVE')
    modeladmin.message_user(request, f'{updated} elemento(s) desactivado(s) correctamente.')

@admin.action(description="📊 Exportar a CSV")
def export_to_csv(modeladmin, request, queryset):
    import csv
    from django.http import HttpResponse
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="export.csv"'
    
    writer = csv.writer(response)
    fields = [field.name for field in queryset.model._meta.fields]
    writer.writerow(fields)
    
    for obj in queryset:
        writer.writerow([getattr(obj, field) for field in fields])
    
    return response

@admin.action(description="🔴 Marcar alertas como resueltas")
def resolve_alerts(modeladmin, request, queryset):
    updated = queryset.update(is_resolved=True)
    modeladmin.message_user(request, f'{updated} alerta(s) marcada(s) como resuelta(s).')

# =========================================================================
# INLINES
# =========================================================================

class ZoneInline(admin.TabularInline):
    model = Zone
    extra = 0
    fields = ('name', 'description', 'state')
    show_change_link = True
    can_delete = True
    verbose_name = "Zona"
    verbose_name_plural = "Zonas"

class DeviceInline(admin.TabularInline):
    model = Device
    extra = 0
    fields = ('name', 'category', 'max_consumption', 'state')
    show_change_link = True
    can_delete = False
    verbose_name = "Dispositivo"
    verbose_name_plural = "Dispositivos"
    autocomplete_fields = ['category']
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """
        SCOPING: Limitar opciones de FK según organización
        """
        if db_field.name == "category" and not request.user.is_superuser:
            org = get_user_organization(request.user)
            if org:
                kwargs["queryset"] = Category.objects.filter(organization=org)
        
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

class MeasurementInline(admin.TabularInline):
    model = Measurement
    extra = 0
    fields = ('measurement_date', 'consumption_value', 'notes', 'state')
    readonly_fields = ('measurement_date', 'consumption_value')
    can_delete = False
    max_num = 5
    ordering = ('-measurement_date',)
    verbose_name = "Última Medición"
    verbose_name_plural = "Últimas 5 Mediciones"

class AlertInline(admin.TabularInline):
    model = Alert
    extra = 0
    fields = ('severity', 'message', 'is_resolved', 'created_at')
    readonly_fields = ('severity', 'message', 'created_at')
    can_delete = False
    max_num = 5
    ordering = ('-created_at',)
    verbose_name = "Alerta Reciente"
    verbose_name_plural = "Últimas 5 Alertas"

# =========================================================================
# MAESTROS GLOBALES (Catálogos) - CON SCOPING
# =========================================================================

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'organization', 'device_count', 'state', 'created_at')
    search_fields = ('name', 'description', 'organization__name')
    list_filter = ('state', 'organization', 'created_at')
    ordering = ('organization', 'name')
    list_select_related = ('organization',)
    list_per_page = 50
    readonly_fields = ('created_at', 'updated_at')
    actions = [make_active, make_inactive, export_to_csv]
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('name', 'description', 'organization')
        }),
        ('Imagen', {
            'fields': ('icon',),
            'classes': ('collapse',)
        }),
        ('Estado', {
            'fields': ('state',)
        }),
        ('Metadatos', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def device_count(self, obj):
        count = Device.objects.filter(category=obj).count()
        return format_html('<span style="color: blue;">{} dispositivo(s)</span>', count)
    device_count.short_description = 'Dispositivos'
    
    # =====================================================================
    # SCOPING: Filtrar por organización
    # =====================================================================
    
    def get_queryset(self, request):
        """Filtrar categorías por organización del usuario"""
        qs = super().get_queryset(request)
        
        if request.user.is_superuser:
            return qs
        
        org = get_user_organization(request.user)
        if org:
            return qs.filter(organization=org)
        
        return qs.none()
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Limitar opciones de organización"""
        if db_field.name == "organization" and not request.user.is_superuser:
            org = get_user_organization(request.user)
            if org:
                kwargs["queryset"] = Organization.objects.filter(id=org.id)
                kwargs["initial"] = org.id
        
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

# =========================================================================
# POR ORGANIZACIÓN - CON SCOPING
# =========================================================================

@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'zone_count', 'device_count', 'state')
    search_fields = ('name', 'email', 'address')
    list_filter = ('state', 'created_at')
    ordering = ('name',)
    list_per_page = 50
    readonly_fields = ('created_at', 'updated_at')
    inlines = [ZoneInline]
    actions = [make_active, make_inactive, export_to_csv]
    
    fieldsets = (
        ('Información de la Empresa', {
            'fields': ('name', 'email', 'phone', 'address')
        }),
        ('Logo', {
            'fields': ('logo',),
            'classes': ('collapse',)
        }),
        ('Estado', {
            'fields': ('state',)
        }),
        ('Metadatos', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def zone_count(self, obj):
        count = Zone.objects.filter(organization=obj).count()
        return f'{count} zona(s)'
    zone_count.short_description = 'Zonas'
    
    def device_count(self, obj):
        count = Device.objects.filter(organization=obj).count()
        return f'{count} dispositivo(s)'
    device_count.short_description = 'Dispositivos'
    
    # =====================================================================
    # SCOPING: Solo superusuario ve todas las organizaciones
    # =====================================================================
    
    def get_queryset(self, request):
        """Usuarios normales solo ven su organización"""
        qs = super().get_queryset(request)
        
        if request.user.is_superuser:
            return qs
        
        org = get_user_organization(request.user)
        if org:
            return qs.filter(id=org.id)
        
        return qs.none()
    
    def has_add_permission(self, request):
        """Solo superusuario puede crear organizaciones"""
        return request.user.is_superuser
    
    def has_delete_permission(self, request, obj=None):
        """Solo superusuario puede eliminar organizaciones"""
        return request.user.is_superuser

@admin.register(Zone)
class ZoneAdmin(admin.ModelAdmin):
    list_display = ('name', 'organization', 'device_count', 'state', 'created_at')
    search_fields = ('name', 'description', 'organization__name')
    list_filter = ('state', 'organization', 'created_at')
    ordering = ('organization', 'name')
    list_select_related = ('organization',)
    list_per_page = 50
    readonly_fields = ('created_at', 'updated_at')
    inlines = [DeviceInline]
    actions = [make_active, make_inactive, export_to_csv]
    
    fieldsets = (
        ('Información de la Zona', {
            'fields': ('name', 'description', 'organization')
        }),
        ('Plano', {
            'fields': ('floor_plan',),
            'classes': ('collapse',)
        }),
        ('Estado', {
            'fields': ('state',)
        }),
        ('Metadatos', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def device_count(self, obj):
        count = Device.objects.filter(zone=obj).count()
        return format_html('<strong>{}</strong> dispositivo(s)', count)
    device_count.short_description = 'Dispositivos'
    
    # =====================================================================
    # SCOPING: Filtrar zonas por organización
    # =====================================================================
    
    def get_queryset(self, request):
        """Filtrar zonas por organización del usuario"""
        qs = super().get_queryset(request)
        
        if request.user.is_superuser:
            return qs
        
        org = get_user_organization(request.user)
        if org:
            return qs.filter(organization=org)
        
        return qs.none()
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Limitar opciones de FKs según organización"""
        if not request.user.is_superuser:
            org = get_user_organization(request.user)
            
            if db_field.name == "organization" and org:
                kwargs["queryset"] = Organization.objects.filter(id=org.id)
                kwargs["initial"] = org.id
        
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = (
        'name', 
        'category', 
        'zone', 
        'organization', 
        'max_consumption_display',
        'last_measurement',
        'alert_count',
        'state'
    )
    
    search_fields = (
        'name', 
        'description', 
        'category__name', 
        'zone__name',
        'organization__name'
    )
    
    list_filter = (
        'state', 
        'category', 
        'zone', 
        'organization',
        'created_at'
    )
    
    ordering = ('organization', 'zone', 'name')
    list_select_related = ('category', 'zone', 'organization')
    list_per_page = 50
    readonly_fields = ('created_at', 'updated_at')
    inlines = [MeasurementInline, AlertInline]
    actions = [make_active, make_inactive, export_to_csv]
    
    fieldsets = (
        ('Información del Dispositivo', {
            'fields': ('name', 'description', 'category', 'zone', 'organization')
        }),
        ('Consumo', {
            'fields': ('max_consumption',),
            'description': 'Consumo máximo permitido en kW'
        }),
        ('Imagen', {
            'fields': ('imagen',),
            'classes': ('collapse',)
        }),
        ('Estado', {
            'fields': ('state',)
        }),
        ('Metadatos', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def max_consumption_display(self, obj):
        if obj.max_consumption > 10:
            color = 'red'
        elif obj.max_consumption > 5:
            color = 'orange'
        else:
            color = 'green'
        return format_html('<span style="color: {};">{} kW</span>', color, obj.max_consumption)
    max_consumption_display.short_description = 'Consumo Máximo'
    max_consumption_display.admin_order_field = 'max_consumption'
    
    def last_measurement(self, obj):
        last = Measurement.objects.filter(device=obj).order_by('-measurement_date').first()
        if last:
            return f'{last.consumption_value} kW'
        return '-'
    last_measurement.short_description = 'Última Medición'
    
    def alert_count(self, obj):
        count = Alert.objects.filter(device=obj, is_resolved=False).count()
        if count > 0:
            return format_html('<span style="color: red; font-weight: bold;">⚠️ {}</span>', count)
        return '✓'
    alert_count.short_description = 'Alertas'
    
    # =====================================================================
    # SCOPING: Filtrar dispositivos por organización
    # =====================================================================
    
    def get_queryset(self, request):
        """Filtrar dispositivos por organización del usuario"""
        qs = super().get_queryset(request)
        
        if request.user.is_superuser:
            return qs
        
        org = get_user_organization(request.user)
        if org:
            return qs.filter(organization=org)
        
        return qs.none()
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """
        SCOPING CRÍTICO: Limitar opciones de FKs según organización
        Esto evita que un usuario pueda asignar dispositivos a otras organizaciones
        """
        if not request.user.is_superuser:
            org = get_user_organization(request.user)
            
            if db_field.name == "organization" and org:
                # Solo su organización
                kwargs["queryset"] = Organization.objects.filter(id=org.id)
                kwargs["initial"] = org.id
            
            elif db_field.name == "zone" and org:
                # Solo zonas de su organización
                kwargs["queryset"] = Zone.objects.filter(organization=org)
            
            elif db_field.name == "category" and org:
                # Solo categorías de su organización
                kwargs["queryset"] = Category.objects.filter(organization=org)
        
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    
    def has_change_permission(self, request, obj=None):
        """Verificar que el dispositivo pertenece a su organización"""
        has_perm = super().has_change_permission(request, obj)
        
        if not has_perm or request.user.is_superuser:
            return has_perm
        
        if obj is not None:
            org = get_user_organization(request.user)
            return org and obj.organization == org
        
        return has_perm
    
    def has_delete_permission(self, request, obj=None):
        """Verificar que el dispositivo pertenece a su organización"""
        has_perm = super().has_delete_permission(request, obj)
        
        if not has_perm or request.user.is_superuser:
            return has_perm
        
        if obj is not None:
            org = get_user_organization(request.user)
            return org and obj.organization == org
        
        return has_perm

# =========================================================================
# SERIES / DATOS OPERACIONALES - CON SCOPING
# =========================================================================

@admin.register(Measurement)
class MeasurementAdmin(admin.ModelAdmin):
    list_display = (
        'device',
        'consumption_display',
        'measurement_date',
        'organization',
        'exceeds_limit',
        'state'
    )
    
    search_fields = (
        'device__name',
        'notes',
        'organization__name'
    )
    
    list_filter = (
        'state',
        'measurement_date',
        'organization',
        'device__category'
    )
    
    ordering = ('-measurement_date',)
    date_hierarchy = 'measurement_date'
    list_select_related = ('device', 'organization', 'device__category', 'device__zone')
    list_per_page = 100
    readonly_fields = ('created_at', 'updated_at')
    actions = [make_active, make_inactive, export_to_csv]
    
    fieldsets = (
        ('Medición', {
            'fields': ('device', 'consumption_value', 'measurement_date', 'organization')
        }),
        ('Notas', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        ('Estado', {
            'fields': ('state',)
        }),
        ('Metadatos', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def consumption_display(self, obj):
        if obj.consumption_value > obj.device.max_consumption:
            return format_html('<span style="color: red; font-weight: bold;">{} kW ⚠️</span>', 
                             obj.consumption_value)
        return f'{obj.consumption_value} kW'
    consumption_display.short_description = 'Consumo'
    consumption_display.admin_order_field = 'consumption_value'
    
    def exceeds_limit(self, obj):
        if obj.consumption_value > obj.device.max_consumption:
            return format_html('<span style="color: red;">⚠️ Excede</span>')
        return format_html('<span style="color: green;">✓ Normal</span>')
    exceeds_limit.short_description = 'Estado'
    
    # =====================================================================
    # SCOPING: Filtrar mediciones por organización
    # =====================================================================
    
    def get_queryset(self, request):
        """Filtrar mediciones por organización del usuario"""
        qs = super().get_queryset(request)
        
        if request.user.is_superuser:
            return qs
        
        org = get_user_organization(request.user)
        if org:
            return qs.filter(organization=org)
        
        return qs.none()
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Limitar opciones de FKs según organización"""
        if not request.user.is_superuser:
            org = get_user_organization(request.user)
            
            if db_field.name == "device" and org:
                kwargs["queryset"] = Device.objects.filter(organization=org)
            
            elif db_field.name == "organization" and org:
                kwargs["queryset"] = Organization.objects.filter(id=org.id)
                kwargs["initial"] = org.id
        
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = (
        'device',
        'severity_display',
        'message_short',
        'is_resolved_display',
        'created_at',
        'organization'
    )
    
    search_fields = (
        'device__name',
        'message',
        'organization__name'
    )
    
    list_filter = (
        'severity',
        'is_resolved',
        'state',
        'organization',
        'created_at'
    )
    
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'
    list_select_related = ('device', 'measurement', 'organization')
    list_per_page = 100
    readonly_fields = ('created_at', 'updated_at')
    actions = [resolve_alerts, make_active, make_inactive, export_to_csv]
    
    fieldsets = (
        ('Alerta', {
            'fields': ('device', 'measurement', 'severity', 'message', 'organization')
        }),
        ('Resolución', {
            'fields': ('is_resolved',)
        }),
        ('Estado', {
            'fields': ('state',)
        }),
        ('Metadatos', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def severity_display(self, obj):
        colors_emojis = {
            'CRITICAL': ('#dc3545', '🔴'),
            'HIGH': ('#fd7e14', '🟠'),
            'MEDIUM': ('#ffc107', '🟡'),
            'LOW': ('#28a745', '🟢')
        }
        color, emoji = colors_emojis.get(obj.severity, ('#6c757d', '⚪'))
        return format_html('<span style="color: {}; font-weight: bold;">{} {}</span>', 
                          color, emoji, obj.get_severity_display())
    severity_display.short_description = 'Severidad'
    severity_display.admin_order_field = 'severity'
    
    def message_short(self, obj):
        if len(obj.message) > 50:
            return obj.message[:50] + '...'
        return obj.message
    message_short.short_description = 'Mensaje'
    
    def is_resolved_display(self, obj):
        if obj.is_resolved:
            return format_html('<span style="color: green;">✅ Resuelta</span>')
        return format_html('<span style="color: red;">❌ Pendiente</span>')
    is_resolved_display.short_description = 'Estado'
    is_resolved_display.admin_order_field = 'is_resolved'
    
    # =====================================================================
    # SCOPING: Filtrar alertas por organización
    # =====================================================================
    
    def get_queryset(self, request):
        """Filtrar alertas por organización del usuario"""
        qs = super().get_queryset(request)
        
        if request.user.is_superuser:
            return qs
        
        org = get_user_organization(request.user)
        if org:
            return qs.filter(organization=org)
        
        return qs.none()
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Limitar opciones de FKs según organización"""
        if not request.user.is_superuser:
            org = get_user_organization(request.user)
            
            if db_field.name == "device" and org:
                kwargs["queryset"] = Device.objects.filter(organization=org)
            
            elif db_field.name == "measurement" and org:
                kwargs["queryset"] = Measurement.objects.filter(organization=org)
            
            elif db_field.name == "organization" and org:
                kwargs["queryset"] = Organization.objects.filter(id=org.id)
                kwargs["initial"] = org.id
        
        return super().formfield_for_foreignkey(db_field, request, **kwargs)