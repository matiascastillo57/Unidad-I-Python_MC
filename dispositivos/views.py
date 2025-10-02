from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.db.models import Count, Avg, Sum, Q, F
from .models import Dispositivo, Medicion, Alerta, Categoria, Zona

def inicio(request):
    """Vista principal con resumen del sistema"""
    # Datos de resumen
    total_dispositivos = Dispositivo.objects.filter(estado='ACTIVO').count()
    dispositivos_criticos = Dispositivo.objects.filter(
        estado='ACTIVO',
        consumo_actual__gt=F('consumo_max')
    ).count()
    
    # Dispositivos recientes
    dispositivos_recientes = Dispositivo.objects.filter(estado='ACTIVO')[:5]
    
    # Alertas no resueltas
    alertas_pendientes = Alerta.objects.filter(resuelta=False, estado='ACTIVO').count()
    
    contexto = {
        'total_dispositivos': total_dispositivos,
        'dispositivos_criticos': dispositivos_criticos,
        'dispositivos_recientes': dispositivos_recientes,
        'alertas_pendientes': alertas_pendientes,
    }
    
    return render(request, 'inicio.html', contexto)

def panel_dispositivos(request):
    """Panel principal de dispositivos como pide el ejercicio"""
    dispositivos = Dispositivo.objects.filter(estado='ACTIVO').select_related('categoria', 'zona')
    
    # Contar dispositivos críticos
    dispositivos_criticos = 0
    for dispositivo in dispositivos:
        if not dispositivo.esta_en_limite():
            dispositivos_criticos += 1
    
    contexto = {
        'dispositivos': dispositivos,
        'dispositivos_criticos': dispositivos_criticos,
        'total_dispositivos': dispositivos.count(),
    }
    
    return render(request, 'dispositivos/lista.html', contexto)

def detalle_dispositivo(request, id):
    """Detalle de un dispositivo específico"""
    dispositivo = get_object_or_404(Dispositivo, id=id)
    
    # Últimas 10 mediciones
    mediciones = dispositivo.mediciones.filter(estado='ACTIVO')[:10]
    
    # Alertas del dispositivo
    alertas = dispositivo.alertas.filter(estado='ACTIVO')[:5]
    
    # Estadísticas
    promedio_consumo = dispositivo.mediciones.filter(estado='ACTIVO').aggregate(
        promedio=Avg('consumo')
    )['promedio'] or 0
    
    contexto = {
        'dispositivo': dispositivo,
        'mediciones': mediciones,
        'alertas': alertas,
        'promedio_consumo': round(promedio_consumo, 1),
    }
    
    return render(request, 'dispositivos/detalle.html', contexto)

def lista_mediciones(request):
    """Lista todas las mediciones del sistema"""
    mediciones = Medicion.objects.filter(estado='ACTIVO').select_related('dispositivo')[:50]
    
    contexto = {
        'mediciones': mediciones,
    }
    
    return render(request, 'mediciones/lista.html', contexto)