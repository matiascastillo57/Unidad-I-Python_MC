#!/usr/bin/env python
import os
import sys
import django
from datetime import datetime, timedelta
from decimal import Decimal

sys.path.append('/var/www/django/ecoenergy')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecoenergy.settings')
django.setup()

from django.contrib.auth.models import User, Group
from monitoring.models import Zone, Category, Device, Measurement, Organization

def main():
    print("=" * 60)
    print("🚀 POBLANDO BASE DE DATOS")
    print("=" * 60)
    
    try:
        # 1. Obtener organización
        org = Organization.objects.first()
        if not org:
            print("❌ No hay organizaciones")
            return
        
        print(f"🏢 Usando: {org.name}")
        
        # 2. Crear zonas
        print("\n🗺️  Zonas...")
        zonas_data = [
            ('Sala Reuniones Norte', 'Conferencias'),
            ('Área Producción', 'Manufactura'),
            ('Bodega Principal', 'Almacenamiento'),
            ('Laboratorio I+D', 'Investigación'),
        ]
        
        for nombre, desc in zonas_data:
            z, created = Zone.objects.get_or_create(
                name=nombre,
                organization=org,
                defaults={'description': desc}
            )
            print(f"   {'✓' if created else '-'} {nombre}")
        
        # 3. Obtener datos base
        zonas = list(Zone.objects.all())
        categorias = list(Category.objects.all())
        
        if not zonas or not categorias:
            print("⚠️  Faltan zonas o categorías")
            return
        
        # 4. Crear dispositivos
        print("\n💡 Dispositivos...")
        
        dispositivos_data = [
            {
                'name': 'Router Cisco RV340',
                'description': 'Router de red principal',
                'category': categorias[0],
                'zone': zonas[0],
                'organization': org,
                'max_consumption': Decimal('0.15'),
            },
            {
                'name': 'Switch 48 Puertos',
                'description': 'Switch de distribución',
                'category': categorias[0],
                'zone': zonas[0],
                'organization': org,
                'max_consumption': Decimal('0.35'),
            },
            {
                'name': 'AC 18K BTU',
                'description': 'Sistema de climatización',
                'category': categorias[min(1, len(categorias)-1)],
                'zone': zonas[min(1, len(zonas)-1)],
                'organization': org,
                'max_consumption': Decimal('2.20'),
            },
            {
                'name': 'Panel LED 100W',
                'description': 'Iluminación LED',
                'category': categorias[min(2, len(categorias)-1)] if len(categorias) > 2 else categorias[0],
                'zone': zonas[min(2, len(zonas)-1)] if len(zonas) > 2 else zonas[0],
                'organization': org,
                'max_consumption': Decimal('0.10'),
            },
            {
                'name': 'Workstation Dell',
                'description': 'Estación de trabajo',
                'category': categorias[0],
                'zone': zonas[min(3, len(zonas)-1)] if len(zonas) > 3 else zonas[0],
                'organization': org,
                'max_consumption': Decimal('0.45'),
            },
        ]
        
        for disp_data in dispositivos_data:
            d, created = Device.objects.get_or_create(
                name=disp_data['name'],
                defaults=disp_data
            )
            print(f"   {'✓' if created else '-'} {d.name}")
        
        # 5. Crear mediciones con campos correctos
        print("\n📊 Mediciones...")
        dispositivos = Device.objects.all()
        fecha_inicio = datetime.now() - timedelta(days=7)
        contador = 0
        
        import random
        for dispositivo in dispositivos:
            for dia in range(7):
                for hora in [0, 6, 12, 18]:
                    fecha = (fecha_inicio + timedelta(days=dia)).replace(
                        hour=hora, minute=0, second=0, microsecond=0
                    )
                    
                    consumo = float(dispositivo.max_consumption) * random.uniform(0.6, 0.95)
                    
                    _, created = Measurement.objects.get_or_create(
                        device=dispositivo,
                        measurement_date=fecha,
                        organization=org,
                        defaults={
                            'consumption_value': Decimal(str(round(consumo, 2))),
                            'notes': 'Medición automática'
                        }
                    )
                    if created:
                        contador += 1
        
        print(f"   ✓ {contador} mediciones")
        
        # 6. Crear usuarios
        print("\n👥 Usuarios...")
        
        Group.objects.get_or_create(name='Administradores')
        editor_g, _ = Group.objects.get_or_create(name='Editores')
        viewer_g, _ = Group.objects.get_or_create(name='Lectores')
        
        usuarios = [
            ('maria.silva', 'Editor2024!', 'María', 'Silva', editor_g, True),
            ('carlos.lopez', 'Lector2024!', 'Carlos', 'López', viewer_g, False),
        ]
        
        for username, pwd, first, last, group, staff in usuarios:
            u, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': f'{username}@ecoenergy.com',
                    'first_name': first,
                    'last_name': last,
                    'is_staff': staff
                }
            )
            
            if created:
                u.set_password(pwd)
                u.save()
                u.groups.add(group)
                print(f"   ✓ {username} ({group.name})")
            else:
                print(f"   - {username}")
        
        # Resumen
        print("\n" + "=" * 60)
        print("✅ COMPLETADO")
        print("=" * 60)
        print(f"\n📊 Resumen:")
        print(f"   Organizaciones: {Organization.objects.count()}")
        print(f"   Zonas: {Zone.objects.count()}")
        print(f"   Categorías: {Category.objects.count()}")
        print(f"   Dispositivos: {Device.objects.count()}")
        print(f"   Mediciones: {Measurement.objects.count()}")
        print(f"   Usuarios: {User.objects.count()}")
        print()
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
