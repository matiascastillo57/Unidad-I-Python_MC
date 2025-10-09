"""
Management command para crear roles, módulos, permisos y usuarios
Uso: python manage.py seed_roles
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from usuarios.models import UserProfile
from monitoring.models import Organization, Device, Measurement, Alert

class Command(BaseCommand):
    help = 'Crea roles, permisos y usuarios para el sistema'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Iniciando creación de roles y usuarios...'))

        try:
            with transaction.atomic():
                
                # ============================================================
                # 1. CREAR/OBTENER ORGANIZACIÓN
                # ============================================================
                self.stdout.write('Creando organización...')
                
                org, created = Organization.objects.get_or_create(
                    name='EcoTech Solutions',
                    defaults={
                        'email': 'contacto@ecotech.cl',
                        'phone': '+56 2 2345 6789',
                        'address': 'Av. Providencia 1234, Santiago'
                    }
                )
                
                if created:
                    self.stdout.write(self.style.SUCCESS(f'✓ Organización creada: {org.name}'))
                else:
                    self.stdout.write(f'✓ Organización existente: {org.name}')

                # ============================================================
                # 2. CREAR GRUPOS (ROLES)
                # ============================================================
                self.stdout.write('\nCreando grupos/roles...')
                
                # Rol: Admin Cliente (acceso completo)
                group_admin, created = Group.objects.get_or_create(name='Admin Cliente')
                if created:
                    self.stdout.write('  ✓ Grupo "Admin Cliente" creado')
                
                # Rol: Operador (solo mediciones)
                group_operador, created = Group.objects.get_or_create(name='Operador')
                if created:
                    self.stdout.write('  ✓ Grupo "Operador" creado')
                
                # Rol: Consulta (solo lectura)
                group_consulta, created = Group.objects.get_or_create(name='Consulta')
                if created:
                    self.stdout.write('  ✓ Grupo "Consulta" creado')

                # ============================================================
                # 3. ASIGNAR PERMISOS DE DJANGO A GRUPOS
                # ============================================================
                self.stdout.write('\nAsignando permisos a grupos...')
                
                # Obtener content types
                ct_device = ContentType.objects.get_for_model(Device)
                ct_measurement = ContentType.objects.get_for_model(Measurement)
                ct_alert = ContentType.objects.get_for_model(Alert)
                
                # Admin Cliente: TODOS los permisos
                perms_admin = Permission.objects.filter(
                    content_type__in=[ct_device, ct_measurement, ct_alert]
                )
                group_admin.permissions.set(perms_admin)
                self.stdout.write(f'  ✓ Admin Cliente: {perms_admin.count()} permisos')
                
                # Operador: Solo view y add de mediciones, view de devices
                perms_operador = Permission.objects.filter(
                    content_type=ct_measurement,
                    codename__in=['view_measurement', 'add_measurement']
                ) | Permission.objects.filter(
                    content_type=ct_device,
                    codename='view_device'
                ) | Permission.objects.filter(
                    content_type=ct_alert,
                    codename='view_alert'
                )
                group_operador.permissions.set(perms_operador)
                self.stdout.write(f'  ✓ Operador: {perms_operador.count()} permisos')
                
                # Consulta: Solo view de todo
                perms_consulta = Permission.objects.filter(
                    content_type__in=[ct_device, ct_measurement, ct_alert],
                    codename__startswith='view_'
                )
                group_consulta.permissions.set(perms_consulta)
                self.stdout.write(f'  ✓ Consulta: {perms_consulta.count()} permisos')

                # ============================================================
                # 4. CREAR USUARIOS
                # ============================================================
                self.stdout.write('\nCreando usuarios...')
                
                # Usuario 1: Admin Cliente
                user_admin, created = User.objects.get_or_create(
                    username='admin_cliente',
                    defaults={
                        'email': 'admin@ecotech.cl',
                        'first_name': 'Admin',
                        'last_name': 'Cliente',
                        'is_staff': True,
                        'is_active': True
                    }
                )
                
                if created:
                    user_admin.set_password('admin123')
                    user_admin.save()
                    self.stdout.write('  ✓ Usuario "admin_cliente" creado')
                else:
                    self.stdout.write('  ✓ Usuario "admin_cliente" ya existe')
                
                # Asignar grupo
                user_admin.groups.clear()
                user_admin.groups.add(group_admin)
                
                # Crear/actualizar perfil
                profile_admin, created = UserProfile.objects.get_or_create(
                    user=user_admin,
                    defaults={
                        'organization': org,
                        'position': 'Administrador',
                        'rut': '12345678-9',
                        'phone': '+56 9 8888 8888'
                    }
                )
                if not created:
                    profile_admin.organization = org
                    profile_admin.save()
                
                # Usuario 2: Operador
                user_operador, created = User.objects.get_or_create(
                    username='operador_1',
                    defaults={
                        'email': 'operador@ecotech.cl',
                        'first_name': 'María',
                        'last_name': 'González',
                        'is_staff': True,
                        'is_active': True
                    }
                )
                
                if created:
                    user_operador.set_password('operador123')
                    user_operador.save()
                    self.stdout.write('  ✓ Usuario "operador_1" creado')
                else:
                    self.stdout.write('  ✓ Usuario "operador_1" ya existe')
                
                # Asignar grupo
                user_operador.groups.clear()
                user_operador.groups.add(group_operador)
                
                # Crear/actualizar perfil
                profile_operador, created = UserProfile.objects.get_or_create(
                    user=user_operador,
                    defaults={
                        'organization': org,
                        'position': 'Operador de Campo',
                        'rut': '98765432-1',
                        'phone': '+56 9 7777 7777'
                    }
                )
                if not created:
                    profile_operador.organization = org
                    profile_operador.save()
                
                # Usuario 3: Consulta
                user_consulta, created = User.objects.get_or_create(
                    username='consulta_1',
                    defaults={
                        'email': 'consulta@ecotech.cl',
                        'first_name': 'Pedro',
                        'last_name': 'Silva',
                        'is_staff': True,
                        'is_active': True
                    }
                )
                
                if created:
                    user_consulta.set_password('consulta123')
                    user_consulta.save()
                    self.stdout.write('  ✓ Usuario "consulta_1" creado')
                else:
                    self.stdout.write('  ✓ Usuario "consulta_1" ya existe')
                
                # Asignar grupo
                user_consulta.groups.clear()
                user_consulta.groups.add(group_consulta)
                
                # Crear/actualizar perfil
                profile_consulta, created = UserProfile.objects.get_or_create(
                    user=user_consulta,
                    defaults={
                        'organization': org,
                        'position': 'Consultor',
                        'rut': '11223344-5',
                        'phone': '+56 9 6666 6666'
                    }
                )
                if not created:
                    profile_consulta.organization = org
                    profile_consulta.save()

                # ============================================================
                # RESUMEN FINAL
                # ============================================================
                self.stdout.write('\n' + '='*70)
                self.stdout.write(self.style.SUCCESS('ROLES Y USUARIOS CREADOS EXITOSAMENTE'))
                self.stdout.write('='*70)
                
                self.stdout.write('\n📊 RESUMEN:')
                self.stdout.write(f'   Organización: {org.name}')
                self.stdout.write(f'   Grupos: {Group.objects.count()}')
                self.stdout.write(f'   Usuarios: {User.objects.filter(is_staff=True).count()} (staff)')
                
                self.stdout.write('\n👥 USUARIOS CREADOS:')
                self.stdout.write('   1. Admin Cliente:')
                self.stdout.write('      Username: admin_cliente')
                self.stdout.write('      Password: admin123')
                self.stdout.write('      Permisos: COMPLETOS (agregar, editar, eliminar)')
                
                self.stdout.write('\n   2. Operador:')
                self.stdout.write('      Username: operador_1')
                self.stdout.write('      Password: operador123')
                self.stdout.write('      Permisos: Solo agregar mediciones y ver datos')
                
                self.stdout.write('\n   3. Consulta:')
                self.stdout.write('      Username: consulta_1')
                self.stdout.write('      Password: consulta123')
                self.stdout.write('      Permisos: Solo lectura (no puede editar)')
                
                self.stdout.write('\n🔑 MATRIZ DE PERMISOS:')
                self.stdout.write('┌─────────────────┬──────────┬─────────────┬─────────┐')
                self.stdout.write('│ Rol             │ Devices  │ Measurements│ Alerts  │')
                self.stdout.write('├─────────────────┼──────────┼─────────────┼─────────┤')
                self.stdout.write('│ Admin Cliente   │ CRUD     │ CRUD        │ CRUD    │')
                self.stdout.write('│ Operador        │ R        │ CR          │ R       │')
                self.stdout.write('│ Consulta        │ R        │ R           │ R       │')
                self.stdout.write('└─────────────────┴──────────┴─────────────┴─────────┘')
                self.stdout.write('C=Create, R=Read, U=Update, D=Delete')
                
                self.stdout.write('\n✅ Puedes iniciar sesión en /admin/ con cualquiera de estos usuarios')
                self.stdout.write('='*70 + '\n')

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'\n❌ Error: {str(e)}'))
            import traceback
            traceback.print_exc()
            raise