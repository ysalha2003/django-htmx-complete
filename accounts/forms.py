# accounts/forms.py
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.exceptions import ValidationError
from .models import UserProfile
import re

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        help_text="Your email is used for account purposes only.",
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'user@example.com',
            'hx-post': '/accounts/validate/email/',
            'hx-trigger': 'keyup changed delay:500ms',
            'hx-target': '#email-validation',
            'hx-swap': 'innerHTML'
        })
    )
    first_name = forms.CharField(
        max_length=30, 
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter first name',
            'hx-post': '/accounts/validate/first-name/',
            'hx-trigger': 'keyup changed delay:300ms',
            'hx-target': '#first-name-validation',
            'hx-swap': 'innerHTML'
        })
    )
    last_name = forms.CharField(
        max_length=30, 
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter last name',
            'hx-post': '/accounts/validate/last-name/',
            'hx-trigger': 'keyup changed delay:300ms',
            'hx-target': '#last-name-validation',
            'hx-swap': 'innerHTML'
        })
    )
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Enter a unique username',
            'hx-post': '/accounts/validate/username/',
            'hx-trigger': 'keyup changed delay:500ms',
            'hx-target': '#username-validation',
            'hx-swap': 'innerHTML'
        })
        
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Enter a secure password',
            'hx-post': '/accounts/validate/password/',
            'hx-trigger': 'keyup changed delay:300ms',
            'hx-target': '#password-validation',
            'hx-swap': 'innerHTML'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirm new password',
            'hx-post': '/accounts/validate/password2/',
            'hx-trigger': 'keyup changed delay:300ms',
            'hx-target': '#password2-validation',
            'hx-swap': 'innerHTML'
        })
        
        self.fields['username'].help_text = 'Required. Letters, numbers, and @.+-_ only.'
        self.fields['password1'].help_text = None
        self.fields['password2'].help_text = None
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("An account with this email already exists.")
        return email
    
    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')
        if not re.match(r'^[a-zA-Z\s]+$', first_name):
            raise ValidationError("First name can only contain letters and spaces.")
        return first_name
    
    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name')
        if not re.match(r'^[a-zA-Z\s]+$', last_name):
            raise ValidationError("Last name can only contain letters and spaces.")
        return last_name

class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Username or Email',
            'hx-post': '/accounts/validate/login-username/',
            'hx-trigger': 'keyup changed delay:500ms',
            'hx-target': '#login-username-validation',
            'hx-swap': 'innerHTML'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password',
            'hx-post': '/accounts/validate/login-password/',
            'hx-trigger': 'keyup changed delay:300ms',
            'hx-target': '#login-password-validation',
            'hx-swap': 'innerHTML'
        })
    )

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['bio', 'profile_picture', 'birth_date', 'phone_number', 'website', 'location']
        widgets = {
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Enter a brief bio...',
                'maxlength': '500'
            }),
            'profile_picture': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'birth_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+1 (555) 123-4567',
                'hx-post': '/accounts/validate/phone/',
                'hx-trigger': 'keyup changed delay:300ms',
                'hx-target': '#phone-validation',
                'hx-swap': 'innerHTML'
            }),
            'website': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://your-website.com',
                'hx-post': '/accounts/validate/website/',
                'hx-trigger': 'keyup changed delay:500ms',
                'hx-target': '#website-validation',
                'hx-swap': 'innerHTML'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'City, Country'
            })
        }