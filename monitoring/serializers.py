# monitoring/serializers.py
"""
Serializadores para API REST de EcoEnergy
Convierten modelos Django a JSON y viceversa
"""
from rest_framework import serializers
from django.utils import timezone
from .models import Organization, Category, Zone, Device, Measurement, Alert


class OrganizationSerializer(serializers.ModelSerializer):
    """Serializer para Organization"""
    device_count = serializers.SerializerMethodField()
    zone_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Organization
        fields = [
            'id', 
            'name', 
            'email', 
            'phone', 
            'address',
            'state',
            'device_count',
            'zone_count',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_device_count(self, obj):
        """Contar dispositivos activos"""
        return Device.objects.filter(organization=obj, state='ACTIVE').count()
    
    def get_zone_count(self, obj):
        """Contar zonas activas"""
        return Zone.objects.filter(organization=obj, state='ACTIVE').count()


class CategorySerializer(serializers.ModelSerializer):
    """Serializer para Category"""
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    device_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = [
            'id',
            'name',
            'description',
            'organization',
            'organization_name',
            'icon',
            'device_count',
            'state',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_device_count(self, obj):
        """Contar dispositivos en la categoría"""
        return Device.objects.filter(category=obj, state='ACTIVE').count()


class ZoneSerializer(serializers.ModelSerializer):
    """Serializer para Zone"""
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    device_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Zone
        fields = [
            'id',
            'name',
            'description',
            'organization',
            'organization_name',
            'floor_plan',
            'device_count',
            'state',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_device_count(self, obj):
        """Contar dispositivos en la zona"""
        return Device.objects.filter(zone=obj, state='ACTIVE').count()


class DeviceListSerializer(serializers.ModelSerializer):
    """Serializer simple para listado de dispositivos"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    zone_name = serializers.CharField(source='zone.name', read_only=True)
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    
    class Meta:
        model = Device
        fields = [
            'id',
            'name',
            'description',
            'max_consumption',
            'category',
            'category_name',
            'zone',
            'zone_name',
            'organization',
            'organization_name',
            'state',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class DeviceDetailSerializer(serializers.ModelSerializer):
    """Serializer detallado para un dispositivo específico"""
    category = CategorySerializer(read_only=True)
    zone = ZoneSerializer(read_only=True)
    organization = OrganizationSerializer(read_only=True)
    measurement_count = serializers.SerializerMethodField()
    alert_count = serializers.SerializerMethodField()
    avg_consumption = serializers.SerializerMethodField()
    
    class Meta:
        model = Device
        fields = [
            'id',
            'name',
            'description',
            'max_consumption',
            'category',
            'zone',
            'organization',
            'imagen',
            'state',
            'measurement_count',
            'alert_count',
            'avg_consumption',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_measurement_count(self, obj):
        """Contar mediciones del dispositivo"""
        return Measurement.objects.filter(device=obj, state='ACTIVE').count()
    
    def get_alert_count(self, obj):
        """Contar alertas pendientes del dispositivo"""
        return Alert.objects.filter(device=obj, state='ACTIVE', is_resolved=False).count()
    
    def get_avg_consumption(self, obj):
        """Calcular consumo promedio"""
        from django.db.models import Avg
        result = Measurement.objects.filter(
            device=obj, 
            state='ACTIVE'
        ).aggregate(avg=Avg('consumption_value'))
        return round(result['avg'], 2) if result['avg'] else 0.0


class MeasurementSerializer(serializers.ModelSerializer):
    """Serializer para Measurement"""
    device_name = serializers.CharField(source='device.name', read_only=True)
    device_max_consumption = serializers.DecimalField(
        source='device.max_consumption',
        max_digits=10,
        decimal_places=2,
        read_only=True
    )
    exceeds_limit = serializers.SerializerMethodField()
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    
    class Meta:
        model = Measurement
        fields = [
            'id',
            'device',
            'device_name',
            'device_max_consumption',
            'consumption_value',
            'measurement_date',
            'notes',
            'exceeds_limit',
            'organization',
            'organization_name',
            'state',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_exceeds_limit(self, obj):
        """Verificar si excede el límite"""
        return float(obj.consumption_value) > float(obj.device.max_consumption)
    
    def validate_consumption_value(self, value):
        """Validar que el consumo sea positivo"""
        if value <= 0:
            raise serializers.ValidationError("El consumo debe ser mayor a 0 kW.")
        if value > 10000:
            raise serializers.ValidationError("El consumo parece demasiado alto (máximo: 10000 kW).")
        return value
    
    def validate_measurement_date(self, value):
        """Validar que la fecha no sea futura"""
        if value > timezone.now():
            raise serializers.ValidationError("La fecha de medición no puede ser futura.")
        return value


class AlertSerializer(serializers.ModelSerializer):
    """Serializer para Alert"""
    device_name = serializers.CharField(source='device.name', read_only=True)
    device_category = serializers.CharField(source='device.category.name', read_only=True)
    measurement_value = serializers.DecimalField(
        source='measurement.consumption_value',
        max_digits=10,
        decimal_places=2,
        read_only=True
    )
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    
    class Meta:
        model = Alert
        fields = [
            'id',
            'device',
            'device_name',
            'device_category',
            'measurement',
            'measurement_value',
            'severity',
            'message',
            'is_resolved',
            'organization',
            'organization_name',
            'state',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class DashboardStatsSerializer(serializers.Serializer):
    """Serializer para estadísticas del dashboard"""
    total_devices = serializers.IntegerField()
    total_zones = serializers.IntegerField()
    total_measurements = serializers.IntegerField()
    active_alerts = serializers.IntegerField()
    avg_consumption = serializers.DecimalField(max_digits=10, decimal_places=2)
    devices_by_category = serializers.ListField()
    devices_by_zone = serializers.ListField()


class DeviceConsumptionReportSerializer(serializers.Serializer):
    """Serializer para reporte de consumo por dispositivo"""
    device_id = serializers.IntegerField()
    device_name = serializers.CharField()
    total_measurements = serializers.IntegerField()
    avg_consumption = serializers.DecimalField(max_digits=10, decimal_places=2)
    max_consumption = serializers.DecimalField(max_digits=10, decimal_places=2)
    min_consumption = serializers.DecimalField(max_digits=10, decimal_places=2)
    times_exceeded_limit = serializers.IntegerField()