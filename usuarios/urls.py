from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Login usando LoginView (CBV) - SIN formulario personalizado por ahora
    path('login/', auth_views.LoginView.as_view(
        template_name='usuarios/login.html',
        redirect_authenticated_user=True,
    ), name='login'),
    
    # Resto de las URLs...
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', views.user_register, name='register'),
    
    # Password Change
    path('password/change/', auth_views.PasswordChangeView.as_view(
        template_name='usuarios/password_change_form.html',
        success_url='/auth/password/change/done/'
    ), name='password_change'),
    
    path('password/change/done/', auth_views.PasswordChangeDoneView.as_view(
        template_name='usuarios/password_change_done.html'
    ), name='password_change_done'),
    
    # Password Reset
    path('password/reset/', auth_views.PasswordResetView.as_view(
        template_name='usuarios/password_reset_form.html',
        email_template_name='usuarios/email/password_reset_email.txt',
        subject_template_name='usuarios/email/password_reset_subject.txt',
        success_url='/auth/password/reset/done/'
    ), name='password_reset'),
    
    path('password/reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='usuarios/password_reset_done.html'
    ), name='password_reset_done'),
    
    path('password/reset/confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='usuarios/password_reset_confirm.html',
        success_url='/auth/password/reset/complete/'
    ), name='password_reset_confirm'),
    
    path('password/reset/complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name='usuarios/password_reset_complete.html'
    ), name='password_reset_complete'),
]