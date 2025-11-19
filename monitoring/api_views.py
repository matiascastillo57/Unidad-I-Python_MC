# monitoring/api_views.py
"""
ViewSets para API REST de EcoEnergy
Maneja operaciones CRUD vía API
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.views import APIView
from django.db.models import Count, Avg, Max, Min, Q
from django.utils import timezone

from .models import Organization, Category, Zone, Device, Measurement, Alert
from .serializers import (
    OrganizationSerializer,
    CategorySerializer,
    ZoneSerializer,
    DeviceListSerializer,
    DeviceDetailSerializer,
    MeasurementSerializer,
    AlertSerializer,
    DashboardStatsSerializer,
    DeviceConsumptionReportSerializer
)


def get_user_organization(user):
    """Helper para obtener organización del usuario"""
    if user.is_superuser:
        return None
    try:
        return user.userprofile.organization
    except:
        return None


class OrganizationViewSet(viewsets.ModelViewSet):
    """
    ViewSet para Organization
    
    GET /api/organizations/ - Listar todas
    GET /api/organizations/{id}/ - Ver una específica
    POST /api/organizations/ - Crear nueva
    PUT /api/organizations/{id}/ - Actualizar completa
    PATCH /api/organizations/{id}/ - Actualizar parcial
    DELETE /api/organizations/{id}/ - Eliminar
    """
    serializer_class = OrganizationSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        """Filtrar por organización del usuario"""
        user = self.request.user
        
        if not user.is_authenticated:
            return Organization.objects.none()
        
        if user.is_superuser:
            return Organization.objects.filter(state='ACTIVE')
        
        org = get_user_organization(user)
        if org:
            return Organization.objects.filter(id=org.id, state='ACTIVE')
        
        return Organization.objects.none()


class CategoryViewSet(viewsets.ModelViewSet):
    """ViewSet para Category con filtros"""
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        """Filtrar categorías por organización del usuario"""
        user = self.request.user
        
        if not user.is_authenticated:
            return Category.objects.filter(state='ACTIVE')
        
        if user.is_superuser:
            return Category.objects.filter(state='ACTIVE')
        
        org = get_user_organization(user)
        if org:
            return Category.objects.filter(organization=org, state='ACTIVE')
        
        return Category.objects.filter(state='ACTIVE')
    
    @action(detail=True, methods=['get'])
    def devices(self, request, pk=None):
        """
        Endpoint: /api/categories/{id}/devices/
        Retorna dispositivos de una categoría
        """
        category = self.get_object()
        devices = Device.objects.filter(category=category, state='ACTIVE')
        serializer = DeviceListSerializer(devices, many=True)
        return Response(serializer.data)


class ZoneViewSet(viewsets.ModelViewSet):
    """ViewSet para Zone"""
    serializer_class = ZoneSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        """Filtrar zonas por organización del usuario"""
        user = self.request.user
        
        if not user.is_authenticated:
            return Zone.objects.filter(state='ACTIVE')
        
        if user.is_superuser:
            return Zone.objects.filter(state='ACTIVE')
        
        org = get_user_organization(user)
        if org:
            return Zone.objects.filter(organization=org, state='ACTIVE')
        
        return Zone.objects.filter(state='ACTIVE')
    
    @action(detail=True, methods=['get'])
    def devices(self, request, pk=None):
        """
        Endpoint: /api/zones/{id}/devices/
        Retorna dispositivos de una zona
        """
        zone = self.get_object()
        devices = Device.objects.filter(zone=zone, state='ACTIVE')
        serializer = DeviceListSerializer(devices, many=True)
        return Response(serializer.data)


class DeviceViewSet(viewsets.ModelViewSet):
    """
    ViewSet para Device con acciones personalizadas
    """
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get_serializer_class(self):
        """Usar serializer diferente según la acción"""
        if self.action == 'retrieve':
            return DeviceDetailSerializer
        return DeviceListSerializer
    
    def get_queryset(self):
        """Filtrar dispositivos por organización y aplicar filtros"""
        user = self.request.user
        
        # Filtro base
        queryset = Device.objects.filter(state='ACTIVE')
        
        # Scoping por organización
        if user.is_authenticated and not user.is_superuser:
            org = get_user_organization(user)
            if org:
                queryset = queryset.filter(organization=org)
        
        # Filtros por query params
        category_id = self.request.query_params.get('category', None)
        zone_id = self.request.query_params.get('zone', None)
        search = self.request.query_params.get('search', None)
        
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        
        if zone_id:
            queryset = queryset.filter(zone_id=zone_id)
        
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | 
                Q(description__icontains=search)
            )
        
        return queryset.select_related('category', 'zone', 'organization')
    
    @action(detail=True, methods=['get'])
    def measurements(self, request, pk=None):
        """
        Endpoint: /api/devices/{id}/measurements/
        Retorna mediciones de un dispositivo
        
        Parámetros:
        - limit: número máximo de mediciones (default: 50)
        - date_from: filtrar desde esta fecha
        - date_to: filtrar hasta esta fecha
        """
        device = self.get_object()
        
        # Parámetros opcionales
        limit = int(request.query_params.get('limit', 50))
        date_from = request.query_params.get('date_from', None)
        date_to = request.query_params.get('date_to', None)
        
        measurements = Measurement.objects.filter(
            device=device,
            state='ACTIVE'
        )
        
        if date_from:
            measurements = measurements.filter(measurement_date__gte=date_from)
        
        if date_to:
            measurements = measurements.filter(measurement_date__lte=date_to)
        
        measurements = measurements.order_by('-measurement_date')[:limit]
        
        serializer = MeasurementSerializer(measurements, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def alerts(self, request, pk=None):
        """
        Endpoint: /api/devices/{id}/alerts/
        Retorna alertas de un dispositivo (últimas 20)
        """
        device = self.get_object()
        alerts = Alert.objects.filter(
            device=device,
            state='ACTIVE'
        ).order_by('-created_at')[:20]
        
        serializer = AlertSerializer(alerts, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def stats(self, request, pk=None):
        """
        Endpoint: /api/devices/{id}/stats/
        Retorna estadísticas detalladas de un dispositivo
        """
        device = self.get_object()
        
        measurements = Measurement.objects.filter(
            device=device,
            state='ACTIVE'
        )
        
        stats = measurements.aggregate(
            total=Count('id'),
            avg_consumption=Avg('consumption_value'),
            max_consumption=Max('consumption_value'),
            min_consumption=Min('consumption_value')
        )
        
        times_exceeded = measurements.filter(
            consumption_value__gt=device.max_consumption
        ).count()
        
        return Response({
            'device_id': device.id,
            'device_name': device.name,
            'device_max_allowed': float(device.max_consumption),
            'total_measurements': stats['total'] or 0,
            'avg_consumption': round(float(stats['avg_consumption']), 2) if stats['avg_consumption'] else 0.0,
            'max_consumption': float(stats['max_consumption']) if stats['max_consumption'] else 0.0,
            'min_consumption': float(stats['min_consumption']) if stats['min_consumption'] else 0.0,
            'times_exceeded_limit': times_exceeded,
            'percentage_exceeded': round((times_exceeded / max(stats['total'], 1)) * 100, 2) if stats['total'] else 0.0
        })


class MeasurementViewSet(viewsets.ModelViewSet):
    """
    ViewSet para Measurement
    
    GET /api/measurements/ - Listar todas
    POST /api/measurements/ - Crear nueva
    GET /api/measurements/{id}/ - Ver detalle
    PUT /api/measurements/{id}/ - Actualizar
    DELETE /api/measurements/{id}/ - Eliminar
    
    Parámetros de filtrado:
    - device={id}: filtrar por dispositivo
    - date_from={fecha}: desde fecha
    - date_to={fecha}: hasta fecha
    """
    serializer_class = MeasurementSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        """Filtrar mediciones por organización y aplicar filtros"""
        user = self.request.user
        
        queryset = Measurement.objects.filter(state='ACTIVE')
        
        # Scoping por organización
        if user.is_authenticated and not user.is_superuser:
            org = get_user_organization(user)
            if org:
                queryset = queryset.filter(organization=org)
        
        # Filtros
        device_id = self.request.query_params.get('device', None)
        date_from = self.request.query_params.get('date_from', None)
        date_to = self.request.query_params.get('date_to', None)
        
        if device_id:
            queryset = queryset.filter(device_id=device_id)
        
        if date_from:
            queryset = queryset.filter(measurement_date__gte=date_from)
        
        if date_to:
            queryset = queryset.filter(measurement_date__lte=date_to)
        
        return queryset.select_related('device', 'organization').order_by('-measurement_date')
    
    def perform_create(self, serializer):
        """Al crear, verificar si genera alerta"""
        measurement = serializer.save()
        
        # Generar alerta si excede límite
        if float(measurement.consumption_value) > float(measurement.device.max_consumption):
            Alert.objects.create(
                device=measurement.device,
                measurement=measurement,
                severity='HIGH',
                message=f'Consumo excedido: {measurement.consumption_value} kW (límite: {measurement.device.max_consumption} kW)',
                organization=measurement.organization
            )


class AlertViewSet(viewsets.ModelViewSet):
    """
    ViewSet para Alert
    
    GET /api/alerts/ - Listar todas
    POST /api/alerts/ - Crear nueva
    GET /api/alerts/{id}/ - Ver detalle
    DELETE /api/alerts/{id}/ - Eliminar
    POST /api/alerts/{id}/resolve/ - Marcar como resuelta
    
    Parámetros de filtrado:
    - device={id}: filtrar por dispositivo
    - severity={CRITICAL|HIGH|MEDIUM|LOW}: filtrar por severidad
    - is_resolved={true|false}: filtrar resueltas/pendientes
    """
    serializer_class = AlertSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        """Filtrar alertas por organización y aplicar filtros"""
        user = self.request.user
        
        queryset = Alert.objects.filter(state='ACTIVE')
        
        # Scoping por organización
        if user.is_authenticated and not user.is_superuser:
            org = get_user_organization(user)
            if org:
                queryset = queryset.filter(organization=org)
        
        # Filtros
        device_id = self.request.query_params.get('device', None)
        severity = self.request.query_params.get('severity', None)
        is_resolved = self.request.query_params.get('is_resolved', None)
        
        if device_id:
            queryset = queryset.filter(device_id=device_id)
        
        if severity:
            queryset = queryset.filter(severity=severity)
        
        if is_resolved is not None:
            is_resolved_bool = is_resolved.lower() == 'true'
            queryset = queryset.filter(is_resolved=is_resolved_bool)
        
        return queryset.select_related('device', 'measurement', 'organization').order_by('-created_at')
    
    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        """
        Endpoint: /api/alerts/{id}/resolve/
        POST - Marca una alerta como resuelta
        """
        alert = self.get_object()
        alert.is_resolved = True
        alert.save()
        
        serializer = self.get_serializer(alert)
        return Response(
            {
                'message': 'Alerta marcada como resuelta',
                'alert': serializer.data
            },
            status=status.HTTP_200_OK
        )


class DashboardStatsAPIView(APIView):
    """
    Endpoint: GET /api/dashboard/stats/
    Retorna estadísticas generales del dashboard
    Requiere autenticación
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Obtener estadísticas del dashboard"""
        user = request.user
        org = get_user_organization(user)
        
        # Filtros base
        if user.is_superuser:
            devices = Device.objects.filter(state='ACTIVE')
            zones = Zone.objects.filter(state='ACTIVE')
            measurements = Measurement.objects.filter(state='ACTIVE')
            alerts = Alert.objects.filter(state='ACTIVE')
        elif org:
            devices = Device.objects.filter(organization=org, state='ACTIVE')
            zones = Zone.objects.filter(organization=org, state='ACTIVE')
            measurements = Measurement.objects.filter(organization=org, state='ACTIVE')
            alerts = Alert.objects.filter(organization=org, state='ACTIVE')
        else:
            return Response(
                {'error': 'Usuario sin organización asignada'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Calcular estadísticas
        avg_consumption = measurements.aggregate(avg=Avg('consumption_value'))['avg']
        
        stats = {
            'total_devices': devices.count(),
            'total_zones': zones.count(),
            'total_measurements': measurements.count(),
            'active_alerts': alerts.filter(is_resolved=False).count(),
            'avg_consumption': round(float(avg_consumption), 2) if avg_consumption else 0.0,
            'devices_by_category': list(
                devices.values('category__name')
                .annotate(count=Count('id'))
                .order_by('category__name')
            ),
            'devices_by_zone': list(
                devices.values('zone__name')
                .annotate(count=Count('id'))
                .order_by('zone__name')
            )
        }
        
        serializer = DashboardStatsSerializer(stats)
        return Response(serializer.data)


class HealthCheckAPIView(APIView):
    """
    Endpoint: GET /api/health/
    Health check simple - sin autenticación requerida
    Útil para monitoreo de disponibilidad
    """
    permission_classes = []
    
    def get(self, request):
        """Verificar estado de la API"""
        return Response({
            'status': 'ok',
            'timestamp': timezone.now().isoformat(),
            'version': '1.0.0',
            'service': 'EcoEnergy API'
        }, status=status.HTTP_200_OK)


class ProjectInfoAPIView(APIView):
    """
    Endpoint: GET /api/info/
    Información del proyecto - sin autenticación requerida
    """
    permission_classes = []
    
    def get(self, request):
        """Información del proyecto"""
        return Response({
            'proyecto': 'EcoEnergy',
            'version': '1.0.0',
            'autor': 'Tu Nombre',
            'descripcion': 'Sistema de Monitoreo Energético',
            'tecnologias': [
                'Django 4.2.7',
                'Django Rest Framework',
                'Python 3.11',
                'PostgreSQL/MySQL',
                'AWS'
            ],
            'endpoints_disponibles': {
                'health': '/api/health/',
                'info': '/api/info/',
                'organizations': '/api/organizations/',
                'categories': '/api/categories/',
                'zones': '/api/zones/',
                'devices': '/api/devices/',
                'measurements': '/api/measurements/',
                'alerts': '/api/alerts/',
                'dashboard': '/api/dashboard/stats/'
            }
        }, status=status.HTTP_200_OK)