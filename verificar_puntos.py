# verificar_puntos.py
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecoenergy.settings')
django.setup()

from django.contrib.auth.models import User, Group
from usuarios.models import UserProfile
from monitoring.models import Device, Organization

print("="*60)
print("VERIFICACIÓN DE REQUISITOS PARA 100 PUNTOS")
print("="*60)

# 1. Verificar usuarios
print("\n1. USUARIOS (15 pts):")
users = User.objects.filter(username__in=['admin_cliente', 'operador_1', 'consulta_1'])
print(f"   Usuarios creados: {users.count()}/3")
for user in users:
    groups = user.groups.all()
    print(f"   - {user.username}: grupos={[g.name for g in groups]}, is_staff={user.is_staff}")

# 2. Verificar grupos/roles
print("\n2. GRUPOS/ROLES:")
groups = Group.objects.all()
print(f"   Grupos creados: {groups.count()}")
for group in groups:
    print(f"   - {group.name}: {group.user_set.count()} usuarios")

# 3. Verificar modelos maestros
print("\n3. TABLAS MAESTRAS (10 pts):")
from monitoring.models import Category, Zone
print(f"   Categories: {Category.objects.count()}")
print(f"   Zones: {Zone.objects.count()}")
print(f"   Organizations: {Organization.objects.count()}")

# 4. Verificar modelos operativos
print("\n4. TABLAS OPERATIVAS (10 pts):")
from monitoring.models import Measurement, Alert
print(f"   Devices: {Device.objects.count()}")
print(f"   Measurements: {Measurement.objects.count()}")
print(f"   Alerts: {Alert.objects.count()}")

# 5. Verificar UserProfiles
print("\n5. USER PROFILES:")
profiles = UserProfile.objects.all()
print(f"   Perfiles creados: {profiles.count()}")
for profile in profiles:
    print(f"   - {profile.user.username}: {profile.organization.name}, rol={profile.get_role()}")

print("\n" + "="*60)
print("EJECUCIÓN COMPLETADA")
print("="*60)