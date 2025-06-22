# accounts/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from .forms import CustomUserCreationForm, CustomAuthenticationForm, UserProfileForm
from .models import UserProfile
import re

def is_htmx_request(request):
    """Helper function to check if request is from HTMX"""
    return request.headers.get('HX-Request', False)

class CustomLoginView(LoginView):
    form_class = CustomAuthenticationForm
    template_name = 'registration/login.html'
    
    def form_valid(self, form):
        if is_htmx_request(self.request):
            login(self.request, form.get_user())
            response = HttpResponse()
            response['HX-Redirect'] = self.get_success_url()
            return response
        return super().form_valid(form)
    
    def form_invalid(self, form):
        if is_htmx_request(self.request):
            return render(self.request, 'partials/login_form.html', {'form': form})
        return super().form_invalid(form)

class CustomLogoutView(LogoutView):
    """Custom logout view that handles both GET and POST properly"""
    template_name = 'registration/logout.html'
    
    def dispatch(self, request, *args, **kwargs):
        if request.method == 'GET':
            # Show confirmation page for GET requests
            return render(request, self.template_name)
        # Handle actual logout for POST requests
        return super().dispatch(request, *args, **kwargs)

def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create user profile
            UserProfile.objects.get_or_create(user=user)
            
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            login(request, user)
            
            messages.success(request, f'Account for {user.username} provisioned successfully. Welcome, {user.first_name}!')
            
            if is_htmx_request(request):
                response = HttpResponse()
                response['HX-Redirect'] = reverse_lazy('core:home')
                return response
            
            return redirect('core:home')
        else:
            if is_htmx_request(request):
                return render(request, 'partials/register_form.html', {'form': form})
    
    form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

@login_required
def profile_view(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile state saved successfully.')
            
            if is_htmx_request(request):
                return render(request, 'partials/profile_success.html', {
                    'profile': profile
                })
            
            return redirect('accounts:profile')
        else:
            if is_htmx_request(request):
                return render(request, 'partials/profile_form.html', {
                    'form': form, 
                    'profile': profile
                })
    
    form = UserProfileForm(instance=profile)
    
    context = {
        'form': form,
        'profile': profile
    }
    
    return render(request, 'accounts/profile.html', context)

# Validation Views for Real-time HTMX Validation

@require_http_methods(["POST"])
def validate_username(request):
    username = request.POST.get('username', '').strip()
    
    if not username:
        return HttpResponse('')
    
    if len(username) < 3:
        return render(request, 'partials/validation_error.html', {
            'message': 'Username must be at least 3 characters long'
        })
    
    if len(username) > 150:
        return render(request, 'partials/validation_error.html', {
            'message': 'Username cannot exceed 150 characters'
        })
    
    if not re.match(r'^[a-zA-Z0-9@.+_-]+$', username):
        return render(request, 'partials/validation_error.html', {
            'message': 'Username can only contain letters, numbers, and @.+-_ characters'
        })
    
    if User.objects.filter(username=username).exists():
        return render(request, 'partials/validation_error.html', {
            'message': 'This username is already taken'
        })
    
    return render(request, 'partials/validation_success.html', {
        'message': 'Username is available!'
    })

@require_http_methods(["POST"])
def validate_first_name(request):
    first_name = request.POST.get('first_name', '').strip()
    
    if not first_name:
        return HttpResponse('')
    
    if len(first_name) < 2:
        return render(request, 'partials/validation_error.html', {
            'message': 'First name must be at least 2 characters long'
        })
    
    if not re.match(r'^[a-zA-Z\s]+$', first_name):
        return render(request, 'partials/validation_error.html', {
            'message': 'First name can only contain letters and spaces'
        })
    
    return render(request, 'partials/validation_success.html', {
        'message': 'First name looks good!'
    })

@require_http_methods(["POST"])
def validate_last_name(request):
    last_name = request.POST.get('last_name', '').strip()
    
    if not last_name:
        return HttpResponse('')
    
    if len(last_name) < 2:
        return render(request, 'partials/validation_error.html', {
            'message': 'Last name must be at least 2 characters long'
        })
    
    if not re.match(r'^[a-zA-Z\s]+$', last_name):
        return render(request, 'partials/validation_error.html', {
            'message': 'Last name can only contain letters and spaces'
        })
    
    return render(request, 'partials/validation_success.html', {
        'message': 'Last name looks good!'
    })

@require_http_methods(["POST"])
def validate_email_register(request):
    email = request.POST.get('email', '').strip()
    
    if not email:
        return HttpResponse('')
    
    if User.objects.filter(email=email).exists():
        return render(request, 'partials/validation_error.html', {
            'message': 'An account with this email already exists'
        })
    
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_regex, email):
        return render(request, 'partials/validation_error.html', {
            'message': 'Please enter a valid email address'
        })
    
    return render(request, 'partials/validation_success.html', {
        'message': 'Email is available!'
    })

@require_http_methods(["POST"])
def validate_password(request):
    password = request.POST.get('password1', '').strip()
    
    if not password:
        return HttpResponse('')
    
    strength = 0
    feedback = []
    
    if len(password) >= 8:
        strength += 1
    else:
        feedback.append('At least 8 characters')
    
    if re.search(r'[A-Z]', password):
        strength += 1
    else:
        feedback.append('One uppercase letter')
    
    if re.search(r'[a-z]', password):
        strength += 1
    else:
        feedback.append('One lowercase letter')
    
    if re.search(r'\d', password):
        strength += 1
    else:
        feedback.append('One number')
    
    if re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        strength += 1
    else:
        feedback.append('One special character')
    
    return render(request, 'partials/password_strength.html', {
        'strength': strength,
        'feedback': feedback,
        'password_length': len(password)
    })

@require_http_methods(["POST"])
def validate_password2(request):
    password1 = request.POST.get('password1', '').strip()
    password2 = request.POST.get('password2', '').strip()
    
    if not password2:
        return HttpResponse('')
    
    if password1 != password2:
        return render(request, 'partials/validation_error.html', {
            'message': 'Passwords do not match'
        })
    
    return render(request, 'partials/validation_success.html', {
        'message': 'Passwords match!'
    })

@require_http_methods(["POST"])
def validate_login_username(request):
    username = request.POST.get('username', '').strip()
    
    if not username:
        return HttpResponse('')
    
    if len(username) < 3:
        return render(request, 'partials/validation_error.html', {
            'message': 'Username is too short'
        })
    
    # Check if username exists
    if not User.objects.filter(username=username).exists():
        return render(request, 'partials/validation_warning.html', {
            'message': 'Username not found'
        })
    
    return render(request, 'partials/validation_success.html', {
        'message': 'Username found!'
    })

@require_http_methods(["POST"])
def validate_login_password(request):
    password = request.POST.get('password', '').strip()
    
    if not password:
        return HttpResponse('')
    
    if len(password) < 3:
        return render(request, 'partials/validation_error.html', {
            'message': 'Password is required'
        })
    
    return render(request, 'partials/validation_success.html', {
        'message': 'Password entered'
    })

@require_http_methods(["POST"])
def validate_phone(request):
    phone = request.POST.get('phone_number', '').strip()
    
    if not phone:
        return HttpResponse('')
    
    # Remove all non-digit characters for validation
    digits_only = re.sub(r'[^\d]', '', phone)
    
    if len(digits_only) < 10:
        return render(request, 'partials/validation_error.html', {
            'message': 'Phone number must have at least 10 digits'
        })
    
    if len(digits_only) > 15:
        return render(request, 'partials/validation_error.html', {
            'message': 'Phone number is too long'
        })
    
    return render(request, 'partials/validation_success.html', {
        'message': 'Phone number is valid!'
    })

@require_http_methods(["POST"])
def validate_website(request):
    website = request.POST.get('website', '').strip()
    
    if not website:
        return HttpResponse('')
    
    url_regex = r'^https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)$'
    
    if not re.match(url_regex, website):
        return render(request, 'partials/validation_error.html', {
            'message': 'Please enter a valid URL (include http:// or https://)'
        })
    
    return render(request, 'partials/validation_success.html', {
        'message': 'Website URL is valid!'
    })