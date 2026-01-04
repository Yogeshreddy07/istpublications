from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Q
from .models import EmailLog, EmailTemplate
import logging

logger = logging.getLogger(__name__)


@admin.register(EmailTemplate)
class EmailTemplateAdmin(admin.ModelAdmin):
    """Admin interface for email templates"""
    
    list_display = (
        'name',
        'email_type',
        'is_active_badge',
        'created_at',
        'actions_column'
    )
    list_filter = ('email_type', 'is_active', 'created_at')
    search_fields = ('name', 'subject', 'email_type')
    readonly_fields = ('template_id', 'created_at', 'updated_at', 'variables_display')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('template_id', 'name', 'email_type', 'is_active')
        }),
        ('Email Content', {
            'fields': ('subject', 'body_html', 'body_text')
        }),
        ('Variables & Metadata', {
            'fields': ('variables_display',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def is_active_badge(self, obj):
        """Display active status as colored badge"""
        if obj.is_active:
            return format_html(
                '<span style="background-color: #28a745; color: white; padding: 5px 10px; border-radius: 3px;">Active</span>'
            )
        return format_html(
            '<span style="background-color: #dc3545; color: white; padding: 5px 10px; border-radius: 3px;">Inactive</span>'
        )
    is_active_badge.short_description = 'Status'
    
    def variables_display(self, obj):
        """Display available variables"""
        if not obj.variables:
            return "No variables defined"
        
        html = '<ul style="font-family: monospace; margin: 0;">'
        for var, desc in obj.variables.items():
            html += f'<li><strong>{{{var}}}</strong>: {desc}</li>'
        html += '</ul>'
        return format_html(html)
    variables_display.short_description = 'Available Variables'
    
    def actions_column(self, obj):
        """Quick action buttons"""
        buttons = f'''
        <a class="button" href="/admin/emails/emailtemplate/{obj.id}/change/">Edit</a>
        '''
        return format_html(buttons)
    actions_column.short_description = 'Actions'


@admin.register(EmailLog)
class EmailLogAdmin(admin.ModelAdmin):
    """Admin interface for email logs"""
    
    list_display = (
        'email_id_short',
        'recipient_email',
        'email_type',
        'status_badge',
        'submission_id',
        'sent_at',
        'retry_count',
        'actions_column'
    )
    list_filter = (
        'status',
        'email_type',
        'created_at',
        ('sent_at', admin.EmptyFieldListFilter),
        'retry_count'
    )
    search_fields = ('recipient_email', 'email_id', 'submission_id', 'subject')
    readonly_fields = (
        'email_id',
        'created_at',
        'updated_at',
        'sent_at',
        'failed_reason_display'
    )
    
    fieldsets = (
        ('Email Information', {
            'fields': ('email_id', 'recipient_email', 'sender_email', 'subject')
        }),
        ('Status & Tracking', {
            'fields': ('status', 'email_type', 'submission_id', 'sent_at', 'read_count')
        }),
        ('Retry Information', {
            'fields': ('retry_count', 'failed_reason_display')
        }),
        ('Template & Timestamps', {
            'fields': ('template_used', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def email_id_short(self, obj):
        """Display shortened email ID"""
        return str(obj.email_id)[:8] + "..."
    email_id_short.short_description = 'Email ID'
    
    def status_badge(self, obj):
        """Display status as colored badge"""
        colors = {
            'SENT': '#28a745',
            'FAILED': '#dc3545',
            'PENDING': '#ffc107',
            'BOUNCED': '#fd7e14',
            'OPENED': '#17a2b8',
            'CLICKED': '#007bff',
            'RETRYING': '#6c757d',
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            f'<span style="background-color: {color}; color: white; padding: 5px 10px; border-radius: 3px;">{obj.status}</span>'
        )
    status_badge.short_description = 'Status'
    
    def failed_reason_display(self, obj):
        """Display failed reason in formatted way"""
        if not obj.failed_reason:
            return "N/A"
        return format_html(
            f'<div style="background-color: #fff3cd; padding: 10px; border-radius: 3px; font-family: monospace;">{obj.failed_reason}</div>'
        )
    failed_reason_display.short_description = 'Failure Reason'
    
    def actions_column(self, obj):
        """Quick action buttons"""
        retry_btn = ''
        if obj.status == 'FAILED' and obj.retry_count < 5:
            retry_btn = f'<a class="button" onclick="retryEmail({obj.id})">Retry</a>'
        
        resend_btn = f'<a class="button" href="/admin/emails/emaillog/{obj.id}/resend/">Resend</a>'
        
        return format_html(f'{retry_btn} {resend_btn}')
    actions_column.short_description = 'Actions'
    
    def get_queryset(self, request):
        """Optimize queryset with select_related"""
        qs = super().get_queryset(request)
        return qs.select_related('template_used')
    
    actions = ['mark_as_sent', 'mark_as_failed', 'retry_failed_emails']
    
    def mark_as_sent(self, request, queryset):
        """Admin action to mark emails as sent"""
        count = queryset.update(status='SENT')
        self.message_user(request, f'{count} email(s) marked as sent.')
    mark_as_sent.short_description = "Mark selected as Sent"
    
    def mark_as_failed(self, request, queryset):
        """Admin action to mark emails as failed"""
        count = queryset.update(status='FAILED')
        self.message_user(request, f'{count} email(s) marked as failed.')
    mark_as_failed.short_description = "Mark selected as Failed"
    
    def retry_failed_emails(self, request, queryset):
        """Admin action to retry failed emails"""
        failed = queryset.filter(status='FAILED', retry_count__lt=5)
        count = 0
        for email_log in failed:
            email_log.increment_retry()
            count += 1
        self.message_user(request, f'{count} email(s) queued for retry.')
    retry_failed_emails.short_description = "Retry Failed Emails (max 5 attempts)"
    
    def has_add_permission(self, request):
        """Prevent manual email creation"""
        return False


# Inline admin for email logs in submission
class EmailLogInline(admin.TabularInline):
    """Show email logs in submission admin"""
    model = EmailLog
    extra = 0
    readonly_fields = ('email_id', 'recipient_email', 'status', 'created_at', 'sent_at')
    can_delete = False
    
    fields = ('email_id', 'recipient_email', 'email_type', 'status', 'sent_at')
