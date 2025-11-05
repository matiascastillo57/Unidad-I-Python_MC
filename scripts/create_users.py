# scripts/create_users.py
"""
Script para crear usuarios con diferentes roles y permisos
Ejecutar: python manage.py shell < scripts/create_users.py
"""

from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType
from usuarios.models import UserProfile, Role
from monitoring.models import Organization, Device, Zone, Category, Measurement

print("=" * 60)
print("CREANDO USUARIOS Y ROLES PARA ECOENERGY")
print("=" * 60)

# =========================================================================
# 1. CREAR ORGANIZACIÓN DE PRUEBA
# =========================================================================
print("\n[1/5] Creando organización...")

org, created = Organization.objects.get_or_create(
    name="EcoTech Solutions",
    defaults={
        'email': 'contacto@ecotech.cl',
        'phone': '+56 2 2345 6789',
        'address': 'Av. Providencia 1234, Santiago, Chile',
        'state': 'ACTIVE'
    }
)
print(f"   ✓ Organización: {org.name} {'(creada)' if created else '(ya existía)'}")

# =========================================================================
# 2. CREAR GRUPOS Y ROLES
# =========================================================================
print("\n[2/5] Creando grupos y roles...")

# ADMINISTRADOR
admin_group, created = Group.objects.get_or_create(name='Administrador')
admin_role, created = Role.objects.get_or_create(
    group=admin_group,
    defaults={
        'description': 'Acceso total al sistema. Puede crear, editar y eliminar todo.',
        'is_client_role': True
    }
)
print(f"   ✓ Grupo Administrador {'(creado)' if created else '(ya existía)'}")

# Asignar TODOS los permisos al grupo Administrador
content_types = ContentType.objects.filter(
    app_label__in=['monitoring', 'usuarios']
)
all_permissions = Permission.objects.filter(content_type__in=content_types)
admin_group.permissions.set(all_permissions)
print(f"   ✓ {all_permissions.count()} permisos asignados a Administrador")

# EDITOR
editor_group, created = Group.objects.get_or_create(name='Editor')
editor_role, created = Role.objects.get_or_create(
    group=editor_group,
    defaults={
        'description': 'Puede crear y editar registros, pero no eliminar.',
        'is_client_role': True
    }
)
print(f"   ✓ Grupo Editor {'(creado)' if created else '(ya existía)'}")

# Permisos para Editor: view, add, change (sin delete)
editor_permissions = Permission.objects.filter(
    content_type__in=content_types,
    codename__in=[
        'view_device', 'add_device', 'change_device',
        'view_zone', 'add_zone', 'change_zone',
        'view_category', 'add_category', 'change_category',
        'view_measurement', 'add_measurement', 'change_measurement',
        'view_alert',
    ]
)
editor_group.permissions.set(editor_permissions)
print(f"   ✓ {editor_permissions.count()} permisos asignados a Editor")

# LECTOR
reader_group, created = Group.objects.get_or_create(name='Lector')
reader_role, created = Role.objects.get_or_create(
    group=reader_group,
    defaults={
        'description': 'Solo puede visualizar información, sin crear ni editar.',
        'is_client_role': True
    }
)
print(f"   ✓ Grupo Lector {'(creado)' if created else '(ya existía)'}")

# Permisos para Lector: solo view
reader_permissions = Permission.objects.filter(
    content_type__in=content_types,
    codename__startswith='view_'
)
reader_group.permissions.set(reader_permissions)
print(f"   ✓ {reader_permissions.count()} permisos asignados a Lector")

# =========================================================================
# 3. CREAR USUARIOS
# =========================================================================
print("\n[3/5] Creando usuarios...")

# USUARIO 1: ADMINISTRADOR
if not User.objects.filter(username='admin_ecoenergy').exists():
    admin_user = User.objects.create_user(
        username='admin_ecoenergy',
        email='admin@ecotech.cl',
        password='Admin2025!',
        first_name='Carlos',
        last_name='Administrador',
        is_staff=True
    )
    admin_user.groups.add(admin_group)
    
    UserProfile.objects.create(
        user=admin_user,
        organization=org,
        position='Gerente General',
        phone='+56 9 8888 8888',
        rut='12345678-9'
    )
    print("   ✓ Usuario ADMINISTRADOR creado")
    print("      Usuario: admin_ecoenergy")
    print("      Password: Admin2025!")
    print("      Permisos: CRUD completo")
else:
    print("   ⚠ Usuario admin_ecoenergy ya existe")

# USUARIO 2: EDITOR
if not User.objects.filter(username='editor_ecoenergy').exists():
    editor_user = User.objects.create_user(
        username='editor_ecoenergy',
        email='editor@ecotech.cl',
        password='Editor2025!',
        first_name='María',
        last_name='Editora'
    )
    editor_user.groups.add(editor_group)
    
    UserProfile.objects.create(
        user=editor_user,
        organization=org,
        position='Jefe de Operaciones',
        phone='+56 9 7777 7777',
        rut='98765432-1'
    )
    print("   ✓ Usuario EDITOR creado")
    print("      Usuario: editor_ecoenergy")
    print("      Password: Editor2025!")
    print("      Permisos: Crear y Editar (sin eliminar)")
else:
    print("   ⚠ Usuario editor_ecoenergy ya existe")

# USUARIO 3: LECTOR
if not User.objects.filter(username='lector_ecoenergy').exists():
    reader_user = User.objects.create_user(
        username='lector_ecoenergy',
        email='lector@ecotech.cl',
        password='Lector2025!',
        first_name='Juan',
        last_name='Observador'
    )
    reader_user.groups.add(reader_group)
    
    UserProfile.objects.create(
        user=reader_user,
        organization=org,
        position='Analista',
        phone='+56 9 6666 6666',
        rut='11223344-5'
    )
    print("   ✓ Usuario LECTOR creado")
    print("      Usuario: lector_ecoenergy")
    print("      Password: Lector2025!")
    print("      Permisos: Solo visualizar")
else:
    print("   ⚠ Usuario lector_ecoenergy ya existe")

# =========================================================================
# 4. VERIFICAR PERMISOS
# =========================================================================
print("\n[4/5] Verificando permisos...")

for username in ['admin_ecoenergy', 'editor_ecoenergy', 'lector_ecoenergy']:
    try:
        user = User.objects.get(username=username)
        perms = user.get_all_permissions()
        print(f"   ✓ {username}: {len(perms)} permisos asignados")
    except User.DoesNotExist:
        pass

# =========================================================================
# 5. RESUMEN FINAL
# =========================================================================
print("\n[5/5] Resumen de Credenciales:")
print("=" * 60)
print("\n👤 ADMINISTRADOR (Acceso total)")
print("   Usuario: admin_ecoenergy")
print("   Password: Admin2025!")
print("   Rol: Administrador")
print("   Permisos: Crear, Ver, Editar, Eliminar TODO\n")

print("👤 EDITOR (Crear y Editar)")
print("   Usuario: editor_ecoenergy")
print("   Password: Editor2025!")
print("   Rol: Editor")
print("   Permisos: Crear, Ver, Editar (sin Eliminar)\n")

print("👤 LECTOR (Solo lectura)")
print("   Usuario: lector_ecoenergy")
print("   Password: Lector2025!")
print("   Rol: Lector")
print("   Permisos: Solo Ver\n")

print("=" * 60)
print("✅ USUARIOS CREADOS EXITOSAMENTE")
print("=" * 60)
print("\nPuedes iniciar sesión en: http://localhost:8000/auth/login/")
print("O en AWS: http://tu-ip-publica/auth/login/")