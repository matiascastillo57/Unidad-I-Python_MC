# monitoring/export_views.py
"""
Vistas para exportar datos a Excel (.xlsx)
"""
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from datetime import datetime

from .models import Device, Zone, Category, Measurement


def get_user_organization(user):
    if user.is_superuser:
        return None
    try:
        return user.userprofile.organization
    except:
        return None


@login_required
def export_devices_excel(request):
    """Exportar dispositivos a Excel"""
    organization = get_user_organization(request.user)
    
    # Obtener dispositivos
    if organization:
        devices = Device.objects.filter(organization=organization, state='ACTIVE')
    else:
        devices = Device.objects.filter(state='ACTIVE')
    
    devices = devices.select_related('category', 'zone').order_by('name')
    
    # Crear workbook
    wb = Workbook()
    ws = wb.active
    ws.title = "Dispositivos"
    
    # Estilos
    header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
    header_font = Font(bold=True, color="FFFFFF", size=12)
    
    # Encabezados
    headers = ['ID', 'Nombre', 'Categoría', 'Zona', 'Consumo Máx (kW)', 'Estado', 'Creado']
    ws.append(headers)
    
    # Aplicar estilo a encabezados
    for cell in ws[1]:
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal='center', vertical='center')
    
    # Datos
    for device in devices:
        ws.append([
            device.id,
            device.name,
            device.category.name,
            device.zone.name,
            float(device.max_consumption),
            device.get_state_display(),
            device.created_at.strftime('%d/%m/%Y %H:%M')
        ])
    
    # Ajustar anchos de columna
    ws.column_dimensions['A'].width = 8
    ws.column_dimensions['B'].width = 30
    ws.column_dimensions['C'].width = 20
    ws.column_dimensions['D'].width = 20
    ws.column_dimensions['E'].width = 18
    ws.column_dimensions['F'].width = 12
    ws.column_dimensions['G'].width = 20
    
    # Preparar respuesta HTTP
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    filename = f'dispositivos_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    wb.save(response)
    return response


@login_required
def export_zones_excel(request):
    """Exportar zonas a Excel"""
    organization = get_user_organization(request.user)
    
    if organization:
        zones = Zone.objects.filter(organization=organization, state='ACTIVE')
    else:
        zones = Zone.objects.filter(state='ACTIVE')
    
    zones = zones.order_by('name')
    
    wb = Workbook()
    ws = wb.active
    ws.title = "Zonas"
    
    # Estilos
    header_fill = PatternFill(start_color="70AD47", end_color="70AD47", fill_type="solid")
    header_font = Font(bold=True, color="FFFFFF", size=12)
    
    headers = ['ID', 'Nombre', 'Descripción', 'Organización', 'Estado', 'Creado']
    ws.append(headers)
    
    for cell in ws[1]:
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal='center', vertical='center')
    
    for zone in zones:
        ws.append([
            zone.id,
            zone.name,
            zone.description or '-',
            zone.organization.name,
            zone.get_state_display(),
            zone.created_at.strftime('%d/%m/%Y %H:%M')
        ])
    
    ws.column_dimensions['A'].width = 8
    ws.column_dimensions['B'].width = 25
    ws.column_dimensions['C'].width = 40
    ws.column_dimensions['D'].width = 25
    ws.column_dimensions['E'].width = 12
    ws.column_dimensions['F'].width = 20
    
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    filename = f'zonas_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    wb.save(response)
    return response


@login_required
def export_categories_excel(request):
    """Exportar categorías a Excel"""
    organization = get_user_organization(request.user)
    
    if organization:
        categories = Category.objects.filter(organization=organization, state='ACTIVE')
    else:
        categories = Category.objects.filter(state='ACTIVE')
    
    categories = categories.order_by('name')
    
    wb = Workbook()
    ws = wb.active
    ws.title = "Categorías"
    
    header_fill = PatternFill(start_color="FFC000", end_color="FFC000", fill_type="solid")
    header_font = Font(bold=True, color="000000", size=12)
    
    headers = ['ID', 'Nombre', 'Descripción', 'Organización', 'Estado', 'Creado']
    ws.append(headers)
    
    for cell in ws[1]:
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal='center', vertical='center')
    
    for cat in categories:
        ws.append([
            cat.id,
            cat.name,
            cat.description or '-',
            cat.organization.name,
            cat.get_state_display(),
            cat.created_at.strftime('%d/%m/%Y %H:%M')
        ])
    
    ws.column_dimensions['A'].width = 8
    ws.column_dimensions['B'].width = 25
    ws.column_dimensions['C'].width = 40
    ws.column_dimensions['D'].width = 25
    ws.column_dimensions['E'].width = 12
    ws.column_dimensions['F'].width = 20
    
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    filename = f'categorias_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    wb.save(response)
    return response


@login_required
def export_measurements_excel(request):
    """Exportar mediciones a Excel"""
    organization = get_user_organization(request.user)
    
    if organization:
        measurements = Measurement.objects.filter(organization=organization, state='ACTIVE')
    else:
        measurements = Measurement.objects.filter(state='ACTIVE')
    
    measurements = measurements.select_related('device', 'device__zone').order_by('-measurement_date')[:500]
    
    wb = Workbook()
    ws = wb.active
    ws.title = "Mediciones"
    
    header_fill = PatternFill(start_color="C00000", end_color="C00000", fill_type="solid")
    header_font = Font(bold=True, color="FFFFFF", size=12)
    
    headers = ['ID', 'Dispositivo', 'Zona', 'Consumo (kW)', 'Fecha/Hora', 'Notas', 'Estado']
    ws.append(headers)
    
    for cell in ws[1]:
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal='center', vertical='center')
    
    for m in measurements:
        ws.append([
            m.id,
            m.device.name,
            m.device.zone.name,
            float(m.consumption_value),
            m.measurement_date.strftime('%d/%m/%Y %H:%M:%S'),
            m.notes or '-',
            m.get_state_display()
        ])
    
    ws.column_dimensions['A'].width = 8
    ws.column_dimensions['B'].width = 30
    ws.column_dimensions['C'].width = 20
    ws.column_dimensions['D'].width = 15
    ws.column_dimensions['E'].width = 20
    ws.column_dimensions['F'].width = 40
    ws.column_dimensions['G'].width = 12
    
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    filename = f'mediciones_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    wb.save(response)
    return response