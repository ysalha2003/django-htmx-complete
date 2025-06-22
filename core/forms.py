# core/forms.py
from django import forms
from .models import Contact, NewsletterSubscription
from django.core.validators import RegexValidator
import re

class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ['name', 'email', 'subject', 'category', 'message']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your full name',
                'hx-post': '/validate/name/',
                'hx-trigger': 'keyup changed delay:300ms',
                'hx-target': '#name-validation',
                'hx-swap': 'innerHTML'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'your.email@example.com',
                'hx-post': '/validate/email/',
                'hx-trigger': 'keyup changed delay:500ms',
                'hx-target': '#email-validation',
                'hx-swap': 'innerHTML'
            }),
            'subject': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'What is this about?',
                'hx-post': '/validate/subject/',
                'hx-trigger': 'keyup changed delay:300ms',
                'hx-target': '#subject-validation',
                'hx-swap': 'innerHTML'
            }),
            'category': forms.Select(attrs={
                'class': 'form-select'
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Your detailed message...',
                'hx-post': '/validate/message/',
                'hx-trigger': 'keyup changed delay:500ms',
                'hx-target': '#message-validation',
                'hx-swap': 'innerHTML'
            })
        }
    
    def clean_name(self):
        name = self.cleaned_data.get('name')
        if not re.match(r'^[a-zA-Z\s]+$', name):
            raise forms.ValidationError("Name can only contain letters and spaces.")
        return name

class NewsletterForm(forms.ModelForm):
    class Meta:
        model = NewsletterSubscription
        fields = ['email']
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your email address',
                'hx-post': '/validate/newsletter-email/',
                'hx-trigger': 'keyup changed delay:500ms',
                'hx-target': '#newsletter-validation',
                'hx-swap': 'innerHTML'
            })
        }