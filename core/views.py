# core/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.db.models import Q
from .forms import ContactForm, NewsletterForm
from .models import Contact, NewsletterSubscription
import re

def is_htmx_request(request):
    return request.headers.get('HX-Request', False)

def home(request):
    # Get some stats for the homepage
    total_contacts = Contact.objects.count()
    resolved_contacts = Contact.objects.filter(is_resolved=True).count()
    newsletter_subscribers = NewsletterSubscription.objects.filter(is_active=True).count()
    
    context = {
        'total_contacts': total_contacts,
        'resolved_contacts': resolved_contacts,
        'newsletter_subscribers': newsletter_subscribers,
    }
    
    return render(request, 'core/home.html', context)

def contact_view(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            contact = form.save()
            messages.success(request, f'Inquiry from {contact.name} submitted successfully. Ref: #{contact.id}.')
            
            if is_htmx_request(request):
                return render(request, 'partials/contact_success.html', {
                    'contact': contact
                })
            
            return redirect('core:contact')
        else:
            if is_htmx_request(request):
                return render(request, 'partials/contact_form.html', {'form': form})
    
    form = ContactForm()
    
    # Show recent contacts for staff users
    recent_contacts = None
    if request.user.is_staff:
        recent_contacts = Contact.objects.all()[:5]
    
    context = {
        'form': form,
        'recent_contacts': recent_contacts
    }
    
    return render(request, 'core/contact.html', context)

def newsletter_subscribe(request):
    if request.method == 'POST':
        form = NewsletterForm(request.POST)
        if form.is_valid():
            try:
                subscription = form.save()
                messages.success(request, 'Subscription successful. Thank you for joining our mailing list.')
                
                if is_htmx_request(request):
                    return render(request, 'partials/newsletter_success.html', {
                        'subscription': subscription
                    })
                
                return redirect('core:home')
            except:
                # Email already exists
                messages.warning(request, 'This email address is already subscribed.')
                
                if is_htmx_request(request):
                    return render(request, 'partials/newsletter_warning.html')
        else:
            if is_htmx_request(request):
                return render(request, 'partials/newsletter_form.html', {'form': form})
    
    return redirect('core:home')

@login_required
def contact_list_view(request):
    """Staff-only view to see all contacts"""
    if not request.user.is_staff:
        messages.error(request, 'You do not have permission to view this page.')
        return redirect('core:home')
    
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    
    contacts = Contact.objects.all()
    
    if search_query:
        contacts = contacts.filter(
            Q(name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(subject__icontains=search_query)
        )
    
    if status_filter == 'resolved':
        contacts = contacts.filter(is_resolved=True)
    elif status_filter == 'pending':
        contacts = contacts.filter(is_resolved=False)
    
    paginator = Paginator(contacts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'contacts': page_obj,
        'search_query': search_query,
        'status_filter': status_filter,
    }
    
    return render(request, 'core/contact_list.html', context)

# Validation Views for Contact Form

@require_http_methods(["POST"])
def validate_name(request):
    name = request.POST.get('name', '').strip()
    
    if not name:
        return HttpResponse('')
    
    if len(name) < 2:
        return render(request, 'partials/validation_error.html', {
            'message': 'Name must be at least 2 characters long'
        })
    
    if not re.match(r'^[a-zA-Z\s]+$', name):
        return render(request, 'partials/validation_error.html', {
            'message': 'Name can only contain letters and spaces'
        })
    
    return render(request, 'partials/validation_success.html', {
        'message': 'Name looks good!'
    })

@require_http_methods(["POST"])
def validate_email(request):
    email = request.POST.get('email', '').strip()
    
    if not email:
        return HttpResponse('')
    
    # Check if email already contacted us
    if Contact.objects.filter(email=email).exists():
        return render(request, 'partials/validation_warning.html', {
            'message': 'This email has contacted us before'
        })
    
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_regex, email):
        return render(request, 'partials/validation_error.html', {
            'message': 'Please enter a valid email address'
        })
    
    return render(request, 'partials/validation_success.html', {
        'message': 'Email is valid!'
    })

@require_http_methods(["POST"])
def validate_subject(request):
    subject = request.POST.get('subject', '').strip()
    
    if not subject:
        return HttpResponse('')
    
    if len(subject) < 5:
        return render(request, 'partials/validation_error.html', {
            'message': 'Subject must be at least 5 characters long'
        })
    
    if len(subject) > 200:
        return render(request, 'partials/validation_error.html', {
            'message': 'Subject is too long (max 200 characters)'
        })
    
    return render(request, 'partials/validation_success.html', {
        'message': 'Subject looks good!'
    })

@require_http_methods(["POST"])
def validate_message(request):
    message = request.POST.get('message', '').strip()
    
    if not message:
        return HttpResponse('')
    
    if len(message) < 10:
        return render(request, 'partials/validation_error.html', {
            'message': 'Message must be at least 10 characters long'
        })
    
    word_count = len(message.split())
    char_count = len(message)
    
    return render(request, 'partials/validation_success.html', {
        'message': f'Message looks good! ({word_count} words, {char_count} characters)'
    })

@require_http_methods(["POST"])
def validate_newsletter_email(request):
    email = request.POST.get('email', '').strip()
    
    if not email:
        return HttpResponse('')
    
    if NewsletterSubscription.objects.filter(email=email).exists():
        return render(request, 'partials/validation_warning.html', {
            'message': 'This email is already subscribed'
        })
    
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_regex, email):
        return render(request, 'partials/validation_error.html', {
            'message': 'Please enter a valid email address'
        })
    
    return render(request, 'partials/validation_success.html', {
        'message': 'Email is ready for subscription!'
    })