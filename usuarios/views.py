# usuarios/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.db import transaction
from monitoring.models import Organization
from .models import UserProfile

def user_login(request):
    """
    Vista para el login de usuarios
    """
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # Intentar autenticar al usuario
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Bienvenido, {user.get_full_name() or user.username}!')
            return redirect('dashboard')  # Redirigir al dashboard
        else:
            messages.error(request, 'Usuario o contraseña incorrectos.')
    
    return render(request, 'usuarios/login.html')

def user_register(request):
    """
    Vista para registrar nuevos usuarios y organizaciones
    """
    if request.method == 'POST':
        # Datos de la organización
        organization_name = request.POST.get('organization_name')
        organization_email = request.POST.get('organization_email')
        organization_phone = request.POST.get('organization_phone', '')
        
        # Datos del usuario
        username = request.POST.get('username')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        position = request.POST.get('position', '')
        phone = request.POST.get('phone', '')
        
        # Validaciones básicas
        if not all([organization_name, organization_email, username, email, password]):
            messages.error(request, 'Todos los campos obligatorios deben ser completados.')
            return render(request, 'usuarios/register.html')
        
        if password != password_confirm:
            messages.error(request, 'Las contraseñas no coinciden.')
            return render(request, 'usuarios/register.html')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'El nombre de usuario ya existe.')
            return render(request, 'usuarios/register.html')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'El correo electrónico ya está registrado.')
            return render(request, 'usuarios/register.html')
        
        try:
            with transaction.atomic():
                # Crear organización
                organization = Organization.objects.create(
                    name=organization_name,
                    email=organization_email,
                    phone=organization_phone
                )
                
                # Crear usuario
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    first_name=first_name,
                    last_name=last_name
                )
                
                # Crear perfil de usuario
                UserProfile.objects.create(
                    user=user,
                    organization=organization,
                    phone=phone,
                    position=position
                )
                
                messages.success(request, 'Registro exitoso. Ya puedes iniciar sesión.')
                return redirect('login')
                
        except Exception as e:
            messages.error(request, 'Error al crear la cuenta. Intenta nuevamente.')
    
    return render(request, 'usuarios/register.html')

def user_logout(request):
    """
    Vista para cerrar sesión
    """
    logout(request)
    messages.info(request, 'Sesión cerrada exitosamente.')
    return redirect('login')

def password_reset(request):
    """
    Vista simulada para recuperación de contraseña
    En un proyecto real, esto enviaría un email
    """
    if request.method == 'POST':
        email = request.POST.get('email')
        
        if User.objects.filter(email=email).exists():
            messages.success(request, 
                'Se han enviado las instrucciones de recuperación a tu correo electrónico.')
        else:
            messages.error(request, 'No se encontró una cuenta con ese correo electrónico.')
    
    return render(request, 'usuarios/password_reset.html')