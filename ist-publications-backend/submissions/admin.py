# Django Admin Configuration - Updated Version 2.0
# File: submissions/admin.py
# Enhanced with all form fields and relationships

from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count, Q
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import Author, Submission, SubmissionFile, Reviewer, SubmissionLog, Contact


# ============================================================================
# AUTHOR ADMIN
# ============================================================================

@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = [
        'full_name',
        'email',
        'affiliation_short',
        'role_badge',
        'title',
        'created_at'
    ]
    
    list_filter = [
        'role',
        'title',
        'created_at',
    ]
    
    search_fields = [
        'full_name',
        'email',
        'affiliation',
        'department'
    ]
    
    fieldsets = (
        ('Personal Information', {
            'fields': ('full_name', 'email', 'title')
        }),
        ('Affiliation', {
            'fields': ('affiliation', 'department')
        }),
        ('Role', {
            'fields': ('role',),
            'description': 'Select author, co-author, or reviewer role'
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at', 'id']
    
    def affiliation_short(self, obj):
        """Display truncated affiliation"""
        return obj.affiliation[:50] + '...' if len(obj.affiliation) > 50 else obj.affiliation
    affiliation_short.short_description = 'Affiliation'
    
    def role_badge(self, obj):
        """Display role as colored badge"""
        colors = {
            'author': '#0066CC',      # Blue
            'co-author': '#00AA00',   # Green
            'reviewer': '#CC6600',    # Orange
        }
        color = colors.get(obj.role, '#666666')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 3px; font-weight: bold;">{}</span>',
            color,
            obj.get_role_display()
        )
    role_badge.short_description = 'Role'


# ============================================================================
# SUBMISSION FILE INLINE ADMIN
# ============================================================================

class SubmissionFileInline(admin.TabularInline):
    model = SubmissionFile
    extra = 0
    readonly_fields = [
        'id',
        'file_name',
        'file_type',
        'file_size_display',
        'uploaded_at',
        'created_at'
    ]
    fields = [
        'file',
        'file_name',
        'file_type',
        'file_size_display',
        'uploaded_at'
    ]
    can_delete = True
    
    def file_size_display(self, obj):
        """Display file size in MB"""
        return f"{obj.get_file_size_mb()} MB"
    file_size_display.short_description = 'File Size'


# ============================================================================
# SUBMISSION LOG INLINE ADMIN
# ============================================================================

class SubmissionLogInline(admin.TabularInline):
    model = SubmissionLog
    extra = 0
    readonly_fields = [
        'action',
        'description',
        'performed_by',
        'timestamp'
    ]
    fields = ['action', 'description', 'performed_by', 'timestamp']
    can_delete = False
    
    def has_add_permission(self, request):
        return False


# ============================================================================
# SUBMISSION ADMIN - MAIN INTERFACE
# ============================================================================

@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    
    # List View Configuration
    list_display = [
        'submission_number',
        'title_short',
        'main_author',
        'category_badge',
        'status_badge',
        'file_count',
        'submitted_at_short',
    ]
    
    list_filter = [
        'status',
        'category',
        'copyright_agreed',
        'privacy_agreed',
        'submitted_at',
        'created_at',
    ]
    
    search_fields = [
        'submission_number',
        'title',
        'abstract',
        'keywords',
        'main_author__full_name',
        'main_author__email',
    ]
    
    readonly_fields = [
        'id',
        'submission_number',
        'created_at',
        'updated_at',
        'submitted_at',
        'author_list_display',
        'file_count_display',
    ]
    
    inlines = [
        SubmissionFileInline,
        SubmissionLogInline,
    ]
    
    # Fieldsets
    fieldsets = (
        ('📝 Submission Info', {
            'fields': (
                'id',
                'submission_number',
                'status',
                'title',
            )
        }),
        ('✍️ Authors', {
            'fields': (
                'main_author',
                'author_list_display',
            )
        }),
        ('📋 Article Metadata', {
            'fields': (
                'category',
                'abstract',
                'keywords',
            )
        }),
        ('👥 Suggested Reviewers', {
            'fields': (
                'reviewer_1',
                'reviewer_2',
            ),
            'description': 'Authors can suggest up to 2 peer reviewers'
        }),
        ('✅ Agreements & Policies', {
            'fields': (
                'copyright_agreed',
                'privacy_agreed',
                'corresponding_contact',
            ),
            'classes': ('collapse',)
        }),
        ('📄 Editor Comments', {
            'fields': (
                'editor_comments',
            ),
            'classes': ('collapse',)
        }),
        ('🔍 Admin Notes', {
            'fields': (
                'admin_notes',
            ),
            'classes': ('collapse',)
        }),
        ('📅 Timeline', {
            'fields': (
                'created_at',
                'updated_at',
                'submitted_at',
            ),
            'classes': ('collapse',)
        }),
    )
    
    # Inline admins configured above
    
    # Custom actions
    actions = [
        'mark_under_review',
        'mark_accepted',
        'mark_rejected',
        'mark_revisions_requested',
    ]
    
    def title_short(self, obj):
        """Display truncated title"""
        return obj.title[:60] + '...' if len(obj.title) > 60 else obj.title
    title_short.short_description = 'Title'
    
    def category_badge(self, obj):
        """Display category as badge"""
        colors = {
            'ai': '#FF6B6B',
            'architecture': '#4ECDC4',
            'basic': '#45B7D1',
            'biomedical': '#FFA07A',
            'business': '#98D8C8',
            'cs': '#6C5CE7',
            'data': '#FD79A8',
            'economics': '#A29BFE',
            'engineering': '#74B9FF',
            'management': '#81ECEC',
        }
        color = colors.get(obj.category, '#95A5A6')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; '
            'border-radius: 3px; font-size: 0.85em;">{}</span>',
            color,
            obj.get_category_display()
        )
    category_badge.short_description = 'Category'
    
    def status_badge(self, obj):
        """Display status as colored badge"""
        colors = {
            'draft': '#95A5A6',
            'submitted': '#3498DB',
            'under_review': '#F39C12',
            'accepted': '#27AE60',
            'rejected': '#E74C3C',
            'revisions_requested': '#E67E22',
            'published': '#16A085',
        }
        color = colors.get(obj.status, '#95A5A6')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 5px 10px; '
            'border-radius: 3px; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def file_count(self, obj):
        """Display number of uploaded files"""
        count = obj.files.count()
        color = '#27AE60' if count > 0 else '#E74C3C'
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; '
            'border-radius: 3px; font-weight: bold;">{} file(s)</span>',
            color,
            count
        )
    file_count.short_description = 'Files'
    
    def submitted_at_short(self, obj):
        """Display submission date"""
        if obj.submitted_at:
            return obj.submitted_at.strftime('%Y-%m-%d %H:%M')
        return '—'
    submitted_at_short.short_description = 'Submitted'
    
    def author_list_display(self, obj):
        """Display list of co-authors"""
        co_authors = obj.co_authors.all()
        if co_authors:
            html = '<ul style="margin: 10px 0; padding-left: 20px;">'
            for author in co_authors:
                html += f'<li>{author.full_name} ({author.email})</li>'
            html += '</ul>'
            return mark_safe(html)
        return '—'
    author_list_display.short_description = 'Co-Authors'
    
    def file_count_display(self, obj):
        """Display file count in detail view"""
        count = obj.files.count()
        return f"{count} file(s) uploaded"
    file_count_display.short_description = 'Files'
    
    # Custom actions
    def mark_under_review(self, request, queryset):
        """Mark selected submissions as under review"""
        updated = queryset.update(status='under_review')
        self.message_user(request, f'{updated} submission(s) marked as under review')
    mark_under_review.short_description = 'Mark as Under Review'
    
    def mark_accepted(self, request, queryset):
        """Mark selected submissions as accepted"""
        updated = queryset.update(status='accepted')
        self.message_user(request, f'{updated} submission(s) marked as accepted')
    mark_accepted.short_description = 'Mark as Accepted'
    
    def mark_rejected(self, request, queryset):
        """Mark selected submissions as rejected"""
        updated = queryset.update(status='rejected')
        self.message_user(request, f'{updated} submission(s) marked as rejected')
    mark_rejected.short_description = 'Mark as Rejected'
    
    def mark_revisions_requested(self, request, queryset):
        """Mark submissions as needing revisions"""
        updated = queryset.update(status='revisions_requested')
        self.message_user(request, f'{updated} submission(s) marked as revisions requested')
    mark_revisions_requested.short_description = 'Request Revisions'


# ============================================================================
# REVIEWER ADMIN
# ============================================================================

@admin.register(Reviewer)
class ReviewerAdmin(admin.ModelAdmin):
    
    list_display = [
        'author',
        'submission_short',
        'status_badge',
        'rating_display',
        'due_date',
        'is_overdue_indicator',
    ]
    
    list_filter = [
        'status',
        'rating',
        'due_date',
        'completed_at',
    ]
    
    search_fields = [
        'author__full_name',
        'submission__submission_number',
        'submission__title',
    ]
    
    readonly_fields = [
        'id',
        'created_at',
        'updated_at',
        'is_overdue_indicator',
    ]
    
    fieldsets = (
        ('Review Assignment', {
            'fields': (
                'submission',
                'author',
                'status',
            )
        }),
        ('Timeline', {
            'fields': (
                'invited_at',
                'due_date',
                'completed_at',
                'is_overdue_indicator',
            )
        }),
        ('Review Content', {
            'fields': (
                'rating',
                'comments',
            )
        }),
        ('Metadata', {
            'fields': (
                'id',
                'created_at',
                'updated_at',
            ),
            'classes': ('collapse',)
        }),
    )
    
    def submission_short(self, obj):
        """Display submission number and title"""
        return f"{obj.submission.submission_number} - {obj.submission.title[:40]}..."
    submission_short.short_description = 'Submission'
    
    def status_badge(self, obj):
        """Display status as badge"""
        colors = {
            'invited': '#3498DB',
            'accepted': '#27AE60',
            'rejected': '#E74C3C',
            'completed': '#16A085',
            'pending': '#F39C12',
        }
        color = colors.get(obj.status, '#95A5A6')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; '
            'border-radius: 3px;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def rating_display(self, obj):
        """Display rating with stars"""
        if obj.rating:
            stars = '⭐' * obj.rating
            return format_html('{} ({})', stars, obj.rating)
        return '—'
    rating_display.short_description = 'Rating'
    
    def is_overdue_indicator(self, obj):
        """Show if review is overdue"""
        if obj.is_overdue():
            return format_html(
                '<span style="color: red; font-weight: bold;">⚠️ OVERDUE</span>'
            )
        return '✓ On Track'
    is_overdue_indicator.short_description = 'Status'


# ============================================================================
# SUBMISSION FILE ADMIN
# ============================================================================

@admin.register(SubmissionFile)
class SubmissionFileAdmin(admin.ModelAdmin):
    
    list_display = [
        'file_name',
        'file_type_badge',
        'file_size_mb_display',
        'submission_short',
        'uploaded_at',
    ]
    
    list_filter = [
        'file_type',
        'uploaded_at',
    ]
    
    search_fields = [
        'file_name',
        'submission__submission_number',
        'submission__title',
    ]
    
    readonly_fields = [
        'id',
        'file_name',
        'file_type',
        'file_size',
        'uploaded_at',
        'created_at',
    ]
    
    fieldsets = (
        ('File Information', {
            'fields': (
                'file_name',
                'file_type',
                'file_size',
            )
        }),
        ('Associated Submission', {
            'fields': (
                'submission',
            )
        }),
        ('File Content', {
            'fields': (
                'file',
            )
        }),
        ('Metadata', {
            'fields': (
                'id',
                'uploaded_at',
                'created_at',
            ),
            'classes': ('collapse',)
        }),
    )
    
    def file_type_badge(self, obj):
        """Display file type as badge"""
        colors = {
            'pdf': '#E74C3C',
            'doc': '#3498DB',
            'docx': '#3498DB',
            'rtf': '#F39C12',
        }
        color = colors.get(obj.file_type, '#95A5A6')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; '
            'border-radius: 3px;">{}</span>',
            color,
            obj.get_file_type_display()
        )
    file_type_badge.short_description = 'Type'
    
    def file_size_mb_display(self, obj):
        """Display file size in MB"""
        return f"{obj.get_file_size_mb()} MB"
    file_size_mb_display.short_description = 'Size'
    
    def submission_short(self, obj):
        """Display submission info"""
        return f"{obj.submission.submission_number} - {obj.submission.title[:40]}..."
    submission_short.short_description = 'Submission'


# ============================================================================
# SUBMISSION LOG ADMIN
# ============================================================================

@admin.register(SubmissionLog)
class SubmissionLogAdmin(admin.ModelAdmin):
    
    list_display = [
        'submission',
        'action_badge',
        'performed_by',
        'timestamp',
    ]
    
    list_filter = [
        'action',
        'timestamp',
    ]
    
    search_fields = [
        'submission__submission_number',
        'description',
        'performed_by',
    ]
    
    readonly_fields = [
        'id',
        'submission',
        'action',
        'description',
        'performed_by',
        'timestamp',
    ]
    
    fieldsets = (
        ('Log Details', {
            'fields': (
                'submission',
                'action',
                'description',
            )
        }),
        ('Additional Info', {
            'fields': (
                'performed_by',
                'timestamp',
            )
        }),
        ('System', {
            'fields': (
                'id',
            ),
            'classes': ('collapse',)
        }),
    )
    
    def action_badge(self, obj):
        """Display action as badge"""
        colors = {
            'created': '#3498DB',
            'updated': '#F39C12',
            'submitted': '#27AE60',
            'status_changed': '#9B59B6',
            'file_added': '#1ABC9C',
            'file_removed': '#E74C3C',
            'reviewer_assigned': '#3498DB',
            'review_completed': '#27AE60',
            'email_sent': '#F39C12',
            'comment_added': '#95A5A6',
        }
        color = colors.get(obj.action, '#95A5A6')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; '
            'border-radius: 3px;">{}</span>',
            color,
            obj.get_action_display()
        )
    action_badge.short_description = 'Action'
    
    def has_add_permission(self, request):
        """Prevent manual log creation"""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Prevent log deletion"""
        return False


# ============================================================================
# CONTACT ADMIN
# ============================================================================

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    
    list_display = [
        'name',
        'email',
        'subject_badge',
        'is_read_indicator',
        'created_at',
    ]
    
    list_filter = [
        'subject',
        'is_read',
        'created_at',
    ]
    
    search_fields = [
        'name',
        'email',
        'message',
    ]
    
    readonly_fields = [
        'id',
        'created_at',
    ]
    
    fieldsets = (
        ('Contact Information', {
            'fields': (
                'name',
                'email',
                'phone',
            )
        }),
        ('Message Details', {
            'fields': (
                'subject',
                'message',
            )
        }),
        ('Status', {
            'fields': (
                'is_read',
            )
        }),
        ('Metadata', {
            'fields': (
                'id',
                'created_at',
            ),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_as_read']
    
    def subject_badge(self, obj):
        """Display subject as badge"""
        colors = {
            'paper_submission': '#3498DB',
            'general_inquiry': '#95A5A6',
            'buy_journal': '#27AE60',
        }
        color = colors.get(obj.subject, '#95A5A6')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; '
            'border-radius: 3px;">{}</span>',
            color,
            obj.get_subject_display()
        )
    subject_badge.short_description = 'Subject'
    
    def is_read_indicator(self, obj):
        """Display read status"""
        if obj.is_read:
            return format_html('<span style="color: green; font-weight: bold;">✓ Read</span>')
        return format_html('<span style="color: red; font-weight: bold;">✗ Unread</span>')
    is_read_indicator.short_description = 'Status'
    
    def mark_as_read(self, request, queryset):
        """Mark selected contacts as read"""
        updated = queryset.update(is_read=True)
        self.message_user(request, f'{updated} message(s) marked as read')
    mark_as_read.short_description = 'Mark selected as read'
