from django.contrib import admin
from .models import Categoria, Zona, Dispositivo, Medicion, Alerta

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'estado', 'created_at']
    list_filter = ['estado']
    search_fields = ['nombre']

@admin.register(Zona)
class ZonaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'estado', 'created_at']
    list_filter = ['estado']
    search_fields = ['nombre']

@admin.register(Dispositivo)
class DispositivoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'categoria', 'zona', 'consumo_actual', 'consumo_max', 'esta_en_limite', 'estado']
    list_filter = ['categoria', 'zona', 'estado']
    search_fields = ['nombre']
    readonly_fields = ['created_at', 'updated_at']
    
    def esta_en_limite(self, obj):
        return "✅" if obj.esta_en_limite() else "⚠️"
    esta_en_limite.short_description = "Dentro del límite"

@admin.register(Medicion)
class MedicionAdmin(admin.ModelAdmin):
    list_display = ['dispositivo', 'consumo', 'fecha_medicion', 'estado']
    list_filter = ['dispositivo', 'fecha_medicion', 'estado']
    search_fields = ['dispositivo__nombre']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(Alerta)
class AlertaAdmin(admin.ModelAdmin):
    list_display = ['dispositivo', 'tipo', 'resuelta', 'fecha_alerta', 'estado']
    list_filter = ['tipo', 'resuelta', 'fecha_alerta', 'estado']
    search_fields = ['dispositivo__nombre', 'mensaje']
    readonly_fields = ['created_at', 'updated_at']