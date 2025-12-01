from django.contrib import admin
from .models import Sensor, Departamento, Evento, Barrera, PerfilUsuario


@admin.register(Departamento)
class DepartamentoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'ubicacion', 'activo', 'total_sensores', 'created_at']
    list_filter = ['activo', 'created_at']
    search_fields = ['nombre', 'descripcion', 'ubicacion']
    ordering = ['nombre']
    
    def total_sensores(self, obj):
        return obj.sensores.count()
    total_sensores.short_description = 'Total Sensores'


@admin.register(Sensor)
class SensorAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'uid_mac', 'estado', 'departamento', 
                    'usuario_asignado', 'created_at']
    list_filter = ['estado', 'departamento', 'created_at']
    search_fields = ['nombre', 'uid_mac', 'descripcion']
    list_per_page = 20
    ordering = ['-created_at']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('nombre', 'uid_mac', 'descripcion')
        }),
        ('Estado y Asignación', {
            'fields': ('estado', 'departamento', 'usuario_asignado')
        }),
        ('Fechas', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Barrera)
class BarreraAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'estado', 'departamento', 'ultima_accion', 'created_at']
    list_filter = ['estado', 'departamento']
    search_fields = ['nombre']
    ordering = ['nombre']
    
    actions = ['abrir_barreras', 'cerrar_barreras']
    
    def abrir_barreras(self, request, queryset):
        for barrera in queryset:
            barrera.abrir()
        self.message_user(request, f'{queryset.count()} barrera(s) abierta(s)')
    abrir_barreras.short_description = 'Abrir barreras seleccionadas'
    
    def cerrar_barreras(self, request, queryset):
        for barrera in queryset:
            barrera.cerrar()
        self.message_user(request, f'{queryset.count()} barrera(s) cerrada(s)')
    cerrar_barreras.short_description = 'Cerrar barreras seleccionadas'


@admin.register(Evento)
class EventoAdmin(admin.ModelAdmin):
    list_display = ['tipo', 'sensor', 'barrera', 'usuario_responsable', 
                    'timestamp', 'ip_origen']
    list_filter = ['tipo', 'timestamp', 'sensor__departamento']
    search_fields = ['descripcion', 'sensor__nombre', 'sensor__uid_mac']
    date_hierarchy = 'timestamp'
    list_per_page = 50
    ordering = ['-timestamp']
    
    fieldsets = (
        ('Información del Evento', {
            'fields': ('tipo', 'descripcion', 'ip_origen')
        }),
        ('Relaciones', {
            'fields': ('sensor', 'barrera', 'usuario_responsable')
        }),
        ('Fecha', {
            'fields': ('timestamp',),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ['timestamp']


@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    list_display = ['user', 'rol', 'departamento', 'telefono', 'created_at']
    list_filter = ['rol', 'departamento', 'created_at']
    search_fields = ['user__username', 'user__email', 'user__first_name', 
                     'user__last_name', 'telefono']
    ordering = ['user__username']
    
    fieldsets = (
        ('Usuario', {
            'fields': ('user',)
        }),
        ('Información de Perfil', {
            'fields': ('rol', 'telefono', 'departamento')
        }),
        ('Fechas', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ['created_at', 'updated_at']