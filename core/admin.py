# core/admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils import timezone
from .models import Contact, NewsletterSubscription

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject_preview', 'category', 'created_at', 'status_display', 'resolved_by_display')
    list_filter = ('category', 'is_resolved', 'created_at', 'resolved_by')
    search_fields = ('name', 'email', 'subject', 'message')
    readonly_fields = ('created_at', 'resolved_at', 'id', 'message_preview')
    list_per_page = 25
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    
    fieldsets = (
        ('Contact Information', {
            'fields': ('id', 'name', 'email', 'category'),
            'classes': ('wide',)
        }),
        ('Message Details', {
            'fields': ('subject', 'message', 'message_preview'),
            'classes': ('wide',)
        }),
        ('Status Management', {
            'fields': ('is_resolved', 'resolved_by', 'resolved_at'),
            'classes': ('wide',),
            'description': 'Manage the resolution status of this contact message.'
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        })
    )
    
    actions = ['mark_resolved', 'mark_unresolved', 'export_selected']
    
    def subject_preview(self, obj):
        """Show truncated subject in list view"""
        return obj.subject[:50] + '...' if len(obj.subject) > 50 else obj.subject
    subject_preview.short_description = 'Subject'
    
    def message_preview(self, obj):
        """Show read-only message preview in detail view"""
        if obj.message:
            return format_html(
                '<div style="max-height: 200px; overflow-y: auto; '
                'padding: 10px; background: #f8f9fa; border-radius: 5px;">{}</div>',
                obj.message
            )
        return "No message content"
    message_preview.short_description = 'Message Preview'
    
    def status_display(self, obj):
        """Enhanced status display with colors and icons"""
        if obj.is_resolved:
            return format_html(
                '<span style="color: #28a745; font-weight: bold;">'
                '<i class="fas fa-check-circle"></i> Resolved</span>'
            )
        return format_html(
            '<span style="color: #dc3545; font-weight: bold;">'
            '<i class="fas fa-clock"></i> Pending</span>'
        )
    status_display.short_description = 'Status'
    
    def resolved_by_display(self, obj):
        """Show who resolved the contact"""
        if obj.resolved_by:
            return format_html(
                '<span style="color: #6c757d;">{}</span>',
                obj.resolved_by.get_full_name() or obj.resolved_by.username
            )
        return format_html('<span style="color: #adb5bd;">—</span>')
    resolved_by_display.short_description = 'Resolved By'
    
    def mark_resolved(self, request, queryset):
        """Mark selected contacts as resolved"""
        count = 0
        for contact in queryset:
            if not contact.is_resolved:
                contact.mark_resolved(user=request.user)
                count += 1
        
        if count == 1:
            message = '1 contact was marked as resolved.'
        else:
            message = f'{count} contacts were marked as resolved.'
        
        self.message_user(request, message)
    mark_resolved.short_description = "✅ Mark selected contacts as resolved"
    
    def mark_unresolved(self, request, queryset):
        """Mark selected contacts as unresolved"""
        count = queryset.filter(is_resolved=True).update(
            is_resolved=False, 
            resolved_at=None, 
            resolved_by=None
        )
        
        if count == 1:
            message = '1 contact was marked as unresolved.'
        else:
            message = f'{count} contacts were marked as unresolved.'
        
        self.message_user(request, message)
    mark_unresolved.short_description = "❌ Mark selected contacts as unresolved"
    
    def export_selected(self, request, queryset):
        """Export selected contacts (placeholder for CSV export)"""
        # This could be expanded to actually export CSV
        count = queryset.count()
        self.message_user(request, f'Export functionality for {count} contacts would be implemented here.')
    export_selected.short_description = "📄 Export selected contacts"
    
    def save_model(self, request, obj, form, change):
        """Auto-set resolved_by when marking as resolved"""
        if change and 'is_resolved' in form.changed_data:
            if obj.is_resolved and not obj.resolved_by:
                obj.resolved_by = request.user
                obj.resolved_at = timezone.now()
            elif not obj.is_resolved:
                obj.resolved_by = None
                obj.resolved_at = None
        super().save_model(request, obj, form, change)

@admin.register(NewsletterSubscription)
class NewsletterSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('email', 'subscribed_at', 'is_active', 'status_display')
    list_filter = ('is_active', 'subscribed_at')
    search_fields = ('email',)
    readonly_fields = ('subscribed_at',)
    actions = ['activate_subscriptions', 'deactivate_subscriptions']
    
    def status_display(self, obj):
        """Show subscription status with colors"""
        if obj.is_active:
            return format_html(
                '<span style="color: #28a745; font-weight: bold;">'
                '<i class="fas fa-check-circle"></i> Active</span>'
            )
        return format_html(
            '<span style="color: #6c757d; font-weight: bold;">'
            '<i class="fas fa-times-circle"></i> Inactive</span>'
        )
    status_display.short_description = 'Status'
    
    def activate_subscriptions(self, request, queryset):
        """Activate selected subscriptions"""
        count = queryset.update(is_active=True)
        self.message_user(request, f'{count} subscription(s) activated.')
    activate_subscriptions.short_description = "✅ Activate selected subscriptions"
    
    def deactivate_subscriptions(self, request, queryset):
        """Deactivate selected subscriptions"""
        count = queryset.update(is_active=False)
        self.message_user(request, f'{count} subscription(s) deactivated.')
    deactivate_subscriptions.short_description = "❌ Deactivate selected subscriptions"