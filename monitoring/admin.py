from django.contrib import admin
from django.db.models import Sum, Avg, Count
from django.utils.html import format_html
from .models import Organization, Category, Zone, Device, Measurement, Alert

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
    """Acción para activar múltiples registros"""
    updated = queryset.update(state='ACTIVE')
    modeladmin.message_user(request, f'{updated} elemento(s) activado(s) correctamente.')

@admin.action(description="❌ Desactivar elementos seleccionados")
def make_inactive(modeladmin, request, queryset):
    """Acción para desactivar múltiples registros"""
    updated = queryset.update(state='INACTIVE')
    modeladmin.message_user(request, f'{updated} elemento(s) desactivado(s) correctamente.')

@admin.action(description="📊 Exportar a CSV")
def export_to_csv(modeladmin, request, queryset):
    """Acción para exportar registros a CSV"""
    import csv
    from django.http import HttpResponse
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="export.csv"'
    
    writer = csv.writer(response)
    # Escribir encabezados
    fields = [field.name for field in queryset.model._meta.fields]
    writer.writerow(fields)
    
    # Escribir datos
    for obj in queryset:
        writer.writerow([getattr(obj, field) for field in fields])
    
    return response

@admin.action(description="🔴 Marcar alertas como resueltas")
def resolve_alerts(modeladmin, request, queryset):
    """Acción para resolver alertas en masa"""
    updated = queryset.update(is_resolved=True)
    modeladmin.message_user(request, f'{updated} alerta(s) marcada(s) como resuelta(s).')

# =========================================================================
# INLINES
# =========================================================================

class ZoneInline(admin.TabularInline):
    """Inline para editar Zonas desde Organization"""
    model = Zone
    extra = 0  # No mostrar filas vacías por defecto
    fields = ('name', 'description', 'state')
    show_change_link = True  # Link para abrir en vista propia
    
    # NO incluir 'organization' en fields - Django lo asigna automáticamente
    can_delete = True
    verbose_name = "Zona"
    verbose_name_plural = "Zonas"

class DeviceInline(admin.TabularInline):
    """Inline para editar Devices desde Zone"""
    model = Device
    extra = 0
    fields = ('name', 'category', 'max_consumption', 'state')
    show_change_link = True
    can_delete = False  # No permitir eliminar desde inline
    verbose_name = "Dispositivo"
    verbose_name_plural = "Dispositivos"
    
    # Optimización
    autocomplete_fields = ['category']  # Búsqueda autocompletada

class MeasurementInline(admin.TabularInline):
    """Inline para ver últimas mediciones desde Device"""
    model = Measurement
    extra = 0
    fields = ('measurement_date', 'consumption_value', 'notes', 'state')
    readonly_fields = ('measurement_date', 'consumption_value')  # Solo lectura
    can_delete = False
    max_num = 5  # Máximo 5 mediciones en el inline
    ordering = ('-measurement_date',)
    verbose_name = "Última Medición"
    verbose_name_plural = "Últimas 5 Mediciones"

class AlertInline(admin.TabularInline):
    """Inline para ver alertas desde Device"""
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
# MAESTROS GLOBALES (Catálogos)
# =========================================================================

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Admin para Categorías de dispositivos"""
    
    list_display = ('name', 'organization', 'device_count', 'state', 'created_at')
    search_fields = ('name', 'description', 'organization__name')
    list_filter = ('state', 'organization', 'created_at')
    ordering = ('organization', 'name')
    list_select_related = ('organization',)
    list_per_page = 50
    readonly_fields = ('created_at', 'updated_at')
    
    # ACCIONES
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
        """Mostrar cantidad de dispositivos en esta categoría"""
        count = Device.objects.filter(category=obj).count()
        return format_html('<span style="color: blue;">{} dispositivo(s)</span>', count)
    device_count.short_description = 'Dispositivos'

# =========================================================================
# POR ORGANIZACIÓN
# =========================================================================

@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    """Admin para Organizaciones con Inline de Zonas"""
    
    list_display = ('name', 'email', 'phone', 'zone_count', 'device_count', 'state')
    search_fields = ('name', 'email', 'address')
    list_filter = ('state', 'created_at')
    ordering = ('name',)
    list_per_page = 50
    readonly_fields = ('created_at', 'updated_at')
    
    # INLINES
    inlines = [ZoneInline]
    
    # ACCIONES
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
        """Contar zonas de esta organización"""
        count = Zone.objects.filter(organization=obj).count()
        return f'{count} zona(s)'
    zone_count.short_description = 'Zonas'
    
    def device_count(self, obj):
        """Contar dispositivos de esta organización"""
        count = Device.objects.filter(organization=obj).count()
        return f'{count} dispositivo(s)'
    device_count.short_description = 'Dispositivos'

@admin.register(Zone)
class ZoneAdmin(admin.ModelAdmin):
    """Admin para Zonas con Inline de Devices"""
    
    list_display = ('name', 'organization', 'device_count', 'state', 'created_at')
    search_fields = ('name', 'description', 'organization__name')
    list_filter = ('state', 'organization', 'created_at')
    ordering = ('organization', 'name')
    list_select_related = ('organization',)
    list_per_page = 50
    readonly_fields = ('created_at', 'updated_at')
    
    # INLINES
    inlines = [DeviceInline]
    
    # ACCIONES
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
        """Contar dispositivos en esta zona"""
        count = Device.objects.filter(zone=obj).count()
        return format_html('<strong>{}</strong> dispositivo(s)', count)
    device_count.short_description = 'Dispositivos'

@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    """Admin para Dispositivos con Inlines de Mediciones y Alertas"""
    
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
    
    # INLINES
    inlines = [MeasurementInline, AlertInline]
    
    # ACCIONES
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
        """Formato con color para consumo"""
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
        """Mostrar última medición"""
        last = Measurement.objects.filter(device=obj).order_by('-measurement_date').first()
        if last:
            return f'{last.consumption_value} kW'
        return '-'
    last_measurement.short_description = 'Última Medición'
    
    def alert_count(self, obj):
        """Contar alertas no resueltas"""
        count = Alert.objects.filter(device=obj, is_resolved=False).count()
        if count > 0:
            return format_html('<span style="color: red; font-weight: bold;">⚠️ {}</span>', count)
        return '✓'
    alert_count.short_description = 'Alertas'

# =========================================================================
# SERIES / DATOS OPERACIONALES
# =========================================================================

@admin.register(Measurement)
class MeasurementAdmin(admin.ModelAdmin):
    """Admin para Mediciones"""
    
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
    
    # ACCIONES
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
        """Formato con color según consumo"""
        if obj.consumption_value > obj.device.max_consumption:
            return format_html('<span style="color: red; font-weight: bold;">{} kW ⚠️</span>', 
                             obj.consumption_value)
        return f'{obj.consumption_value} kW'
    consumption_display.short_description = 'Consumo'
    consumption_display.admin_order_field = 'consumption_value'
    
    def exceeds_limit(self, obj):
        """Indicador visual si excede"""
        if obj.consumption_value > obj.device.max_consumption:
            return format_html('<span style="color: red;">⚠️ Excede</span>')
        return format_html('<span style="color: green;">✓ Normal</span>')
    exceeds_limit.short_description = 'Estado'

@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    """Admin para Alertas con acción de resolver"""
    
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
    
    # ACCIONES
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
        """Mostrar severidad con color y emoji"""
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
        """Mensaje truncado"""
        if len(obj.message) > 50:
            return obj.message[:50] + '...'
        return obj.message
    message_short.short_description = 'Mensaje'
    
    def is_resolved_display(self, obj):
        """Mostrar estado de resolución con color"""
        if obj.is_resolved:
            return format_html('<span style="color: green;">✅ Resuelta</span>')
        return format_html('<span style="color: red;">❌ Pendiente</span>')
    is_resolved_display.short_description = 'Estado'
    is_resolved_display.admin_order_field = 'is_resolved'