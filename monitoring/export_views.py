# monitoring/export_views.py
"""
Vistas para exportar datos a Excel
"""
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

from .models import Zone, Device, Category, Measurement
from ecoenergy.decorators import permission_required_with_message


def get_user_organization(user):
    """Helper para obtener organización del usuario"""
    if user.is_superuser:
        return None
    try:
        return user.userprofile.organization
    except:
        return None


def apply_excel_styles(ws):
    """Aplicar estilos profesionales al Excel"""
    # Estilo para encabezados
    header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
    header_font = Font(bold=True, color="FFFFFF", size=12)
    header_alignment = Alignment(horizontal="center", vertical="center")
    
    # Aplicar a la primera fila
    for cell in ws[1]:
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = header_alignment
    
    # Bordes
    thin_border = Border(
        left=Side(style='thin'),
        right=Side(style='thin'),
        top=Side(style='thin'),
        bottom=Side(style='thin')
    )
    
    # Aplicar bordes a todas las celdas con datos
    for row in ws.iter_rows():
        for cell in row:
            cell.border = thin_border
    
    # Ajustar ancho de columnas
    for column in ws.columns:
        max_length = 0
        column_letter = column[0].column_letter
        for cell in column:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except:
                pass
        adjusted_width = min(max_length + 2, 50)
        ws.column_dimensions[column_letter].width = adjusted_width


@login_required
@permission_required_with_message('monitoring.view_zone')
def export_zones_excel(request):
    """Exportar zonas a Excel"""
    organization = get_user_organization(request.user)
    
    # Obtener datos
    if organization:
        zones = Zone.objects.filter(organization=organization, state='ACTIVE').select_related('organization')
    else:
        zones = Zone.objects.filter(state='ACTIVE').select_related('organization')
    
    # Crear workbook
    wb = Workbook()
    ws = wb.active
    ws.title = "Zonas"
    
    # Headers
    headers = ['ID', 'Nombre', 'Descripción', 'Organización', 'Fecha Creación', 'Estado']
    ws.append(headers)
    
    # Data
    for zone in zones:
        ws.append([
            zone.id,
            zone.name,
            zone.description or '',
            zone.organization.name,
            zone.created_at.strftime('%d/%m/%Y %H:%M'),
            'Activa' if zone.state == 'ACTIVE' else 'Inactiva'
        ])
    
    # Aplicar estilos
    apply_excel_styles(ws)
    
    # Crear response
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    filename = f'zonas_{timezone.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
    response['Content-Disposition'] = f'attachment; filename={filename}'
    
    wb.save(response)
    return response


@login_required
@permission_required_with_message('monitoring.view_device')
def export_devices_excel(request):
    """Exportar dispositivos a Excel"""
    organization = get_user_organization(request.user)
    
    # Obtener datos
    if organization:
        devices = Device.objects.filter(
            organization=organization, 
            state='ACTIVE'
        ).select_related('category', 'zone', 'organization')
    else:
        devices = Device.objects.filter(state='ACTIVE').select_related('category', 'zone', 'organization')
    
    # Crear workbook
    wb = Workbook()
    ws = wb.active
    ws.title = "Dispositivos"
    
    # Headers
    headers = ['ID', 'Nombre', 'Categoría', 'Zona', 'Consumo Máximo (kW)', 'Organización', 'Fecha Creación', 'Estado']
    ws.append(headers)
    
    # Data
    for device in devices:
        ws.append([
            device.id,
            device.name,
            device.category.name,
            device.zone.name,
            float(device.max_consumption),
            device.organization.name,
            device.created_at.strftime('%d/%m/%Y %H:%M'),
            'Activo' if device.state == 'ACTIVE' else 'Inactivo'
        ])
    
    # Aplicar estilos
    apply_excel_styles(ws)
    
    # Crear response
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    filename = f'dispositivos_{timezone.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
    response['Content-Disposition'] = f'attachment; filename={filename}'
    
    wb.save(response)
    return response


@login_required
@permission_required_with_message('monitoring.view_category')
def export_categories_excel(request):
    """Exportar categorías a Excel"""
    organization = get_user_organization(request.user)
    
    # Obtener datos
    if organization:
        categories = Category.objects.filter(organization=organization, state='ACTIVE').select_related('organization')
    else:
        categories = Category.objects.filter(state='ACTIVE').select_related('organization')
    
    # Crear workbook
    wb = Workbook()
    ws = wb.active
    ws.title = "Categorías"
    
    # Headers
    headers = ['ID', 'Nombre', 'Descripción', 'Organización', 'Fecha Creación', 'Estado']
    ws.append(headers)
    
    # Data
    for category in categories:
        ws.append([
            category.id,
            category.name,
            category.description or '',
            category.organization.name,
            category.created_at.strftime('%d/%m/%Y %H:%M'),
            'Activa' if category.state == 'ACTIVE' else 'Inactiva'
        ])
    
    # Aplicar estilos
    apply_excel_styles(ws)
    
    # Crear response
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    filename = f'categorias_{timezone.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
    response['Content-Disposition'] = f'attachment; filename={filename}'
    
    wb.save(response)
    return response


@login_required
@permission_required_with_message('monitoring.view_measurement')
def export_measurements_excel(request):
    """Exportar mediciones a Excel"""
    organization = get_user_organization(request.user)
    
    # Obtener datos
    if organization:
        measurements = Measurement.objects.filter(
            organization=organization, 
            state='ACTIVE'
        ).select_related('device', 'device__zone', 'device__category').order_by('-measurement_date')[:1000]
    else:
        measurements = Measurement.objects.filter(state='ACTIVE').select_related(
            'device', 'device__zone', 'device__category'
        ).order_by('-measurement_date')[:1000]
    
    # Crear workbook
    wb = Workbook()
    ws = wb.active
    ws.title = "Mediciones"
    
    # Headers
    headers = [
        'ID', 'Dispositivo', 'Categoría', 'Zona', 'Consumo (kW)', 
        'Consumo Máximo (kW)', '¿Excede?', 'Fecha Medición', 'Notas'
    ]
    ws.append(headers)
    
    # Data
    for m in measurements:
        excede = 'SÍ' if m.consumption_value > m.device.max_consumption else 'NO'
        ws.append([
            m.id,
            m.device.name,
            m.device.category.name,
            m.device.zone.name,
            float(m.consumption_value),
            float(m.device.max_consumption),
            excede,
            m.measurement_date.strftime('%d/%m/%Y %H:%M:%S'),
            m.notes or ''
        ])
    
    # Aplicar estilos
    apply_excel_styles(ws)
    
    # Colorear filas que exceden límite
    from openpyxl.styles import PatternFill
    red_fill = PatternFill(start_color="FFE6E6", end_color="FFE6E6", fill_type="solid")
    
    for row in ws.iter_rows(min_row=2):  # Saltar header
        if row[6].value == 'SÍ':  # Columna "¿Excede?"
            for cell in row:
                cell.fill = red_fill
    
    # Crear response
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    filename = f'mediciones_{timezone.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
    response['Content-Disposition'] = f'attachment; filename={filename}'
    
    wb.save(response)
    return response