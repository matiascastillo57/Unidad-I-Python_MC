# usuarios/profile_views.py
"""
Vistas para gestión de perfil de usuario
Incluye: edición de datos personales, avatar y cambio de contraseña seguro
"""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django import forms
from django.core.validators import FileExtensionValidator
from .models import UserProfile
import re


class UserProfileForm(forms.ModelForm):
    """Formulario para editar perfil de usuario"""
    first_name = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombres'})
    )
    last_name = forms.CharField(
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Apellidos'})
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'correo@ejemplo.com'})
    )
    
    avatar = forms.ImageField(
        required=False,
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'gif'])],
        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'})
    )
    
    class Meta:
        model = UserProfile
        fields = ['phone', 'position', 'direccion', 'avatar']
        widgets = {
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+56 9 1234 5678'}),
            'position': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Cargo en la empresa'}),
            'direccion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Dirección completa'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if self.user:
            self.fields['first_name'].initial = self.user.first_name
            self.fields['last_name'].initial = self.user.last_name
            self.fields['email'].initial = self.user.email
    
    def clean_avatar(self):
        """Validar tamaño de avatar (máximo 2MB)"""
        avatar = self.cleaned_data.get('avatar')
        
        if avatar:
            if avatar.size > 2 * 1024 * 1024:  # 2MB
                raise forms.ValidationError('La imagen no debe superar los 2MB.')
        
        return avatar
    
    def clean_email(self):
        """Validar que el email no esté en uso por otro usuario"""
        email = self.cleaned_data.get('email')
        
        from django.contrib.auth.models import User
        
        if User.objects.filter(email=email).exclude(id=self.user.id).exists():
            raise forms.ValidationError('Este correo ya está en uso por otro usuario.')
        
        return email
    
    def save(self, commit=True):
        """Guardar cambios en User y UserProfile"""
        profile = super().save(commit=False)
        
        if self.user:
            self.user.first_name = self.cleaned_data.get('first_name', '')
            self.user.last_name = self.cleaned_data.get('last_name', '')
            self.user.email = self.cleaned_data.get('email')
            
            if commit:
                self.user.save()
        
        if commit:
            profile.save()
        
        return profile


class SecurePasswordChangeForm(forms.Form):
    """Formulario de cambio de contraseña con validaciones robustas"""
    old_password = forms.CharField(
        label='Contraseña Actual',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Contraseña actual'})
    )
    new_password1 = forms.CharField(
        label='Nueva Contraseña',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Nueva contraseña'})
    )
    new_password2 = forms.CharField(
        label='Confirmar Contraseña',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirma la nueva contraseña'})
    )
    
    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
    
    def clean_old_password(self):
        """Verificar que la contraseña actual sea correcta"""
        old_password = self.cleaned_data.get('old_password')
        
        if not self.user.check_password(old_password):
            raise forms.ValidationError('La contraseña actual es incorrecta.')
        
        return old_password
    
    def clean_new_password1(self):
        """Validaciones robustas de contraseña"""
        password = self.cleaned_data.get('new_password1')
        
        # Longitud mínima
        if len(password) < 8:
            raise forms.ValidationError('La contraseña debe tener al menos 8 caracteres.')
        
        # Debe contener al menos una mayúscula
        if not re.search(r'[A-Z]', password):
            raise forms.ValidationError('La contraseña debe contener al menos una letra mayúscula.')
        
        # Debe contener al menos un número
        if not re.search(r'\d', password):
            raise forms.ValidationError('La contraseña debe contener al menos un número.')
        
        # Debe contener al menos una letra minúscula
        if not re.search(r'[a-z]', password):
            raise forms.ValidationError('La contraseña debe contener al menos una letra minúscula.')
        
        # No puede ser muy común
        common_passwords = ['12345678', 'Password1', 'Qwerty123', 'Abc12345']
        if password in common_passwords:
            raise forms.ValidationError('Esta contraseña es demasiado común.')
        
        # No puede ser similar al nombre de usuario
        if self.user.username.lower() in password.lower():
            raise forms.ValidationError('La contraseña no puede contener tu nombre de usuario.')
        
        return password
    
    def clean(self):
        """Verificar que las contraseñas coincidan"""
        cleaned_data = super().clean()
        password1 = cleaned_data.get('new_password1')
        password2 = cleaned_data.get('new_password2')
        
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError('Las contraseñas no coinciden.')
        
        return cleaned_data
    
    def save(self, commit=True):
        """Cambiar la contraseña del usuario"""
        password = self.cleaned_data['new_password1']
        self.user.set_password(password)
        
        if commit:
            self.user.save()
        
        return self.user


@login_required
def profile_view(request):
    """Vista del perfil del usuario"""
    try:
        profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        messages.error(request, 'No se encontró el perfil del usuario.')
        return redirect('dashboard')
    
    context = {
        'profile': profile,
        'user': request.user,
    }
    
    return render(request, 'usuarios/profile_view.html', context)


@login_required
def profile_edit(request):
    """Editar perfil de usuario"""
    try:
        profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        messages.error(request, 'No se encontró el perfil del usuario.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile, user=request.user)
        
        if form.is_valid():
            form.save()
            messages.success(request, '✅ Perfil actualizado exitosamente.')
            return redirect('profile_view')
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')
    else:
        form = UserProfileForm(instance=profile, user=request.user)
    
    context = {
        'form': form,
        'profile': profile,
    }
    
    return render(request, 'usuarios/profile_edit.html', context)


@login_required
def password_change_secure(request):
    """Cambio de contraseña con validaciones robustas"""
    if request.method == 'POST':
        form = SecurePasswordChangeForm(request.user, request.POST)
        
        if form.is_valid():
            user = form.save()
            
            # Mantener la sesión activa después del cambio
            update_session_auth_hash(request, user)
            
            messages.success(request, '✅ Contraseña cambiada exitosamente.')
            return redirect('profile_view')
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')
    else:
        form = SecurePasswordChangeForm(request.user)
    
    context = {
        'form': form,
    }
    
    return render(request, 'usuarios/password_change_secure.html', context)