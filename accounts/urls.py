# accounts/urls.py
from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # Authentication
    path('register/', views.register_view, name='register'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    path('profile/', views.profile_view, name='profile'),
    
    # Real-time validation endpoints
    path('validate/username/', views.validate_username, name='validate_username'),
    path('validate/first-name/', views.validate_first_name, name='validate_first_name'),
    path('validate/last-name/', views.validate_last_name, name='validate_last_name'),
    path('validate/email/', views.validate_email_register, name='validate_email'),
    path('validate/password/', views.validate_password, name='validate_password'),
    path('validate/password2/', views.validate_password2, name='validate_password2'),
    path('validate/login-username/', views.validate_login_username, name='validate_login_username'),
    path('validate/login-password/', views.validate_login_password, name='validate_login_password'),
    path('validate/phone/', views.validate_phone, name='validate_phone'),
    path('validate/website/', views.validate_website, name='validate_website'),
]