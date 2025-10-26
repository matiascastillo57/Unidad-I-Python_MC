# monitoring/category_views.py
"""
Vistas CRUD para Category
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseBadRequest
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.db.models import Count, Q
from django import forms

from .models import Category, Device, Organization
from ecoenergy.decorators import permission_required_with_message, ajax_permission_required


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description', 'organization', 'icon']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Climatización'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'organization': forms.Select(attrs={'class': 'form-select'}),
            'icon': forms.FileInput(attrs={'class': 'form-control'})
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user and not user.is_superuser:
            try:
                user_org = user.userprofile.organization
                self.fields['organization'].queryset = Organization.objects.filter(id=user_org.id)
                self.fields['organization'].initial = user_org.id
            except:
                self.fields['organization'].queryset = Organization.objects.none()
    
    def clean_name(self):
        name = self.cleaned_data.get('name')
        organization = self.cleaned_data.get('organization')
        
        if name and organization:
            qs = Category.objects.filter(name__iexact=name, organization=organization, state='ACTIVE')
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise forms.ValidationError(f'Ya existe una categoría "{name}" en esta organización.')
        return name


def get_user_organization(user):
    if user.is_superuser:
        return None
    try:
        return user.userprofile.organization
    except:
        return None


@login_required
@permission_required_with_message('monitoring.view_category')
def category_list(request):
    organization = get_user_organization(request.user)
    
    if not organization:
        categories = Category.objects.filter(state='ACTIVE')
    else:
        categories = Category.objects.filter(organization=organization, state='ACTIVE')
    
    categories = categories.annotate(
        device_count=Count('device', filter=Q(device__state='ACTIVE'))
    ).select_related('organization').order_by('name')
    
    context = {
        'categories': categories,
        'organization': organization,
        'can_add': request.user.has_perm('monitoring.add_category'),
        'can_change': request.user.has_perm('monitoring.change_category'),
        'can_delete': request.user.has_perm('monitoring.delete_category'),
    }
    
    return render(request, 'monitoring/category_list.html', context)


@login_required
@permission_required_with_message('monitoring.add_category')
def category_create(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            category = form.save(commit=False)
            if not request.user.is_superuser:
                try:
                    category.organization = request.user.userprofile.organization
                except:
                    messages.error(request, 'Error: Usuario sin organización')
                    return redirect('category_list')
            category.save()
            messages.success(request, f'✅ Categoría "{category.name}" creada exitosamente.')
            return redirect('category_list')
        else:
            messages.error(request, 'Corrige los errores en el formulario.')
    else:
        form = CategoryForm(user=request.user)
    
    return render(request, 'monitoring/category_form.html', {
        'form': form,
        'title': 'Nueva Categoría',
        'button_text': 'Crear Categoría'
    })


@login_required
@permission_required_with_message('monitoring.change_category')
def category_update(request, pk):
    organization = get_user_organization(request.user)
    
    if organization:
        category = get_object_or_404(Category, pk=pk, organization=organization, state='ACTIVE')
    else:
        category = get_object_or_404(Category, pk=pk, state='ACTIVE')
    
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES, instance=category, user=request.user)
        if form.is_valid():
            category = form.save()
            messages.success(request, f'✅ Categoría "{category.name}" actualizada.')
            return redirect('category_list')
    else:
        form = CategoryForm(instance=category, user=request.user)
    
    return render(request, 'monitoring/category_form.html', {
        'form': form,
        'category': category,
        'title': f'Editar: {category.name}',
        'button_text': 'Guardar Cambios'
    })


@login_required
@require_POST
@ajax_permission_required('monitoring.delete_category')
def category_delete_ajax(request, pk):
    if not request.headers.get("x-requested-with") == "XMLHttpRequest":
        return HttpResponseBadRequest("Solo AJAX")
    
    organization = get_user_organization(request.user)
    
    if organization:
        category = get_object_or_404(Category, pk=pk, organization=organization, state='ACTIVE')
    else:
        category = get_object_or_404(Category, pk=pk, state='ACTIVE')
    
    device_count = Device.objects.filter(category=category, state='ACTIVE').count()
    
    if device_count > 0:
        return JsonResponse({
            'ok': False,
            'message': f'No se puede eliminar "{category.name}" porque tiene {device_count} dispositivo(s).'
        })
    
    nombre = category.name
    category.state = 'INACTIVE'
    category.save()
    
    return JsonResponse({
        'ok': True,
        'message': f'Categoría "{nombre}" eliminada correctamente.'
    })