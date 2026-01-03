from django.contrib import admin
from .models import (
    Submission,
    SubmissionStep1,
    SubmissionStep2,
    SubmissionStep3,
    SubmissionStep4,
    SubmissionStep5,
)

# ============================================================================
# SUBMISSION ADMIN
# ============================================================================
@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('submission_id', 'author_name', 'author_email', 'current_step', 'status', 'created_at')
    list_filter = ('status', 'current_step', 'created_at')
    search_fields = ('submission_id', 'author_name', 'author_email')
    readonly_fields = ('submission_id', 'created_at', 'updated_at', 'submitted_at')
    
    fieldsets = (
        ('Submission Info', {
            'fields': ('submission_id', 'author_name', 'author_email')
        }),
        ('Progress', {
            'fields': ('current_step', 'status', 'is_locked')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'submitted_at')
        }),
    )


@admin.register(SubmissionStep1)
class SubmissionStep1Admin(admin.ModelAdmin):
    list_display = ('submission', 'agrees_to_copyright', 'agrees_to_privacy', 'saved_at')
    list_filter = ('agrees_to_copyright', 'agrees_to_privacy', 'saved_at')
    readonly_fields = ('saved_at',)


@admin.register(SubmissionStep2)
class SubmissionStep2Admin(admin.ModelAdmin):
    list_display = ('submission', 'title', 'category', 'saved_at')
    list_filter = ('category', 'saved_at')
    search_fields = ('title', 'submission__submission_id')
    readonly_fields = ('saved_at',)


@admin.register(SubmissionStep3)
class SubmissionStep3Admin(admin.ModelAdmin):
    list_display = ('submission', 'file_name', 'file_type', 'file_size', 'uploaded_at')
    list_filter = ('file_type', 'uploaded_at')
    search_fields = ('file_name', 'submission__submission_id')
    readonly_fields = ('uploaded_at',)


@admin.register(SubmissionStep4)
class SubmissionStep4Admin(admin.ModelAdmin):
    list_display = ('submission', 'reviewer_number', 'reviewer_name', 'reviewer_email', 'suggested_at')
    list_filter = ('reviewer_number', 'suggested_at')
    search_fields = ('reviewer_name', 'reviewer_email', 'submission__submission_id')
    readonly_fields = ('suggested_at',)


@admin.register(SubmissionStep5)
class SubmissionStep5Admin(admin.ModelAdmin):
    list_display = ('submission', 'final_agrees_copyright', 'final_agrees_privacy', 'confirmed_at')
    list_filter = ('final_agrees_copyright', 'final_agrees_privacy', 'confirmed_at')
    readonly_fields = ('confirmed_at',)
