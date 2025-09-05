# monitoring/admin.py
from django.contrib import admin
from .models import Organization, Category, Zone, Device, Measurement, Alert

@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'phone', 'state', 'created_at']
    list_filter = ['state', 'created_at']
    search_fields = ['name', 'email']

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'organization', 'state', 'created_at']
    list_filter = ['state', 'organization']
    search_fields = ['name']

@admin.register(Zone)
class ZoneAdmin(admin.ModelAdmin):
    list_display = ['name', 'organization', 'state', 'created_at']
    list_filter = ['state', 'organization']
    search_fields = ['name']

@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'zone', 'organization', 'max_consumption', 'state']
    list_filter = ['state', 'category', 'zone', 'organization']
    search_fields = ['name']

@admin.register(Measurement)
class MeasurementAdmin(admin.ModelAdmin):
    list_display = ['device', 'consumption_value', 'measurement_date', 'organization']
    list_filter = ['measurement_date', 'device__category', 'organization']
    search_fields = ['device__name']
    date_hierarchy = 'measurement_date'

@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = ['device', 'severity', 'is_resolved', 'created_at', 'organization']
    list_filter = ['severity', 'is_resolved', 'created_at', 'organization']
    search_fields = ['device__name', 'message']