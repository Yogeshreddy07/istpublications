# Django Models - Updated Based on submit.html Analysis
# File: submissions/models.py
# Version 2.0 - Complete with all form fields

from django.db import models
from django.core.validators import FileExtensionValidator, MinLengthValidator, URLValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
import uuid
import os

# ============================================================================
# AUTHOR MODEL - Represents all authors (main, co-authors, reviewers)
# ============================================================================

class Author(models.Model):
    """
    Represents authors and reviewers for submissions.
    Can be used as main author, co-author, or reviewer depending on context.
    """
    
    ROLE_CHOICES = [
        ('author', 'Main Author'),
        ('co-author', 'Co-Author'),
        ('reviewer', 'Reviewer'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    full_name = models.CharField(
        max_length=100,
        validators=[MinLengthValidator(3)],
        help_text="Full name of the author/reviewer"
    )
    email = models.EmailField(
        unique=False,  # Multiple entries possible (different roles)
        help_text="Email address"
    )
    affiliation = models.CharField(
        max_length=255,
        validators=[MinLengthValidator(5)],
        help_text="University, institution, or organization"
    )
    department = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Department (for reviewers)"
    )
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='author',
        help_text="Author's role in the submission process"
    )
    title = models.CharField(
        max_length=10,
        choices=[
            ('Dr', 'Dr.'),
            ('Prof', 'Prof.'),
            ('Mr', 'Mr.'),
            ('Ms', 'Ms.'),
        ],
        blank=True,
        null=True,
        help_text="Professional title (for reviewers)"
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['full_name']
        verbose_name = 'Author'
        verbose_name_plural = 'Authors'
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['role']),
        ]
    
    def __str__(self):
        return f"{self.full_name} ({self.get_role_display()})"
    
    def clean(self):
        """Validate author data"""
        if len(self.full_name.strip()) < 3:
            raise ValidationError("Author name must be at least 3 characters long")


# ============================================================================
# SUBMISSION MODEL - Main submission record
# ============================================================================

class Submission(models.Model):
    """
    Represents an article submission with all metadata and relationships.
    Handles complete 6-step form data from submit.html
    """
    
    CATEGORY_CHOICES = [
        ('ai', 'Artificial Intelligence and Machine Learning (AI/ML)'),
        ('architecture', 'Architecture and Architectural Design'),
        ('basic', 'Basic Sciences & Mathematics'),
        ('biomedical', 'Biomedical Sciences and Bioengineering'),
        ('business', 'Business Sciences'),
        ('cs', 'Computer Science'),
        ('data', 'Data Sciences'),
        ('economics', 'Economics'),
        ('engineering', 'Engineering and Technology'),
        ('management', 'Management'),
    ]
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('under_review', 'Under Review'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('revisions_requested', 'Revisions Requested'),
        ('published', 'Published'),
    ]
    
    # Primary Key
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Submission Number (auto-generated, unique)
    submission_number = models.CharField(
        max_length=50,
        unique=True,
        editable=False,
        help_text="Auto-generated submission identifier"
    )
    
    # STEP 1: ACCEPTANCE & POLICIES
    corresponding_contact = models.BooleanField(
        default=False,
        help_text="Author wishes to be contacted about this submission"
    )
    copyright_agreed = models.BooleanField(
        default=False,
        help_text="Author agrees to copyright terms"
    )
    privacy_agreed = models.BooleanField(
        default=False,
        help_text="Author agrees to privacy policy"
    )
    editor_comments = models.TextField(
        blank=True,
        null=True,
        help_text="Comments for the editor"
    )
    
    # STEP 2: AUTHOR & METADATA
    main_author = models.ForeignKey(
        Author,
        on_delete=models.PROTECT,
        related_name='submissions_as_main_author',
        help_text="Corresponding/main author"
    )
    co_authors = models.ManyToManyField(
        Author,
        blank=True,
        related_name='submissions_as_co_author',
        help_text="Co-authors (max 4)"
    )
    
    # Article Metadata
    title = models.CharField(
        max_length=300,
        validators=[MinLengthValidator(10)],
        help_text="Article title (min 10 chars, max 300)"
    )
    abstract = models.TextField(
        validators=[MinLengthValidator(150)],
        help_text="Abstract (150-200 words recommended)"
    )
    keywords = models.CharField(
        max_length=500,
        help_text="Keywords (comma-separated, 4-6 recommended)"
    )
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        help_text="Article category"
    )
    
    # STEP 4: REVIEWERS
    reviewer_1 = models.ForeignKey(
        Author,
        on_delete=models.SET_NULL,
        related_name='submissions_as_reviewer_1',
        null=True,
        blank=True,
        limit_choices_to={'role': 'reviewer'},
        help_text="Primary suggested reviewer"
    )
    reviewer_2 = models.ForeignKey(
        Author,
        on_delete=models.SET_NULL,
        related_name='submissions_as_reviewer_2',
        null=True,
        blank=True,
        limit_choices_to={'role': 'reviewer'},
        help_text="Secondary suggested reviewer (optional)"
    )
    
    # Status & Metadata
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft',
        help_text="Current status of the submission"
    )
    admin_notes = models.TextField(
        blank=True,
        null=True,
        help_text="Internal notes (admin only)"
    )
    
    # Timestamps
    submitted_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the submission was finalized"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-submitted_at', '-created_at']
        verbose_name = 'Submission'
        verbose_name_plural = 'Submissions'
        indexes = [
            models.Index(fields=['-submitted_at']),
            models.Index(fields=['status']),
            models.Index(fields=['category']),
            models.Index(fields=['main_author']),
        ]
    
    def __str__(self):
        return f"{self.submission_number} - {self.title[:50]}"
    
    def save(self, *args, **kwargs):
        """Generate submission number on first save"""
        if not self.submission_number:
            # Generate format: IST-YYYY-MMDD-XXXXX (5 random chars)
            from datetime import datetime
            import random
            import string
            
            date_part = datetime.now().strftime('%Y%m%d')
            random_part = ''.join(random.choices(string.digits, k=5))
            self.submission_number = f"IST-{date_part}-{random_part}"
        
        super().save(*args, **kwargs)
    
    def mark_submitted(self):
        """Mark submission as officially submitted"""
        self.status = 'submitted'
        self.submitted_at = timezone.now()
        self.save(update_fields=['status', 'submitted_at'])
    
    def get_all_authors(self):
        """Get list of all authors (main + co-authors)"""
        authors = [self.main_author]
        authors.extend(self.co_authors.all())
        return authors
    
    def clean(self):
        """Validate submission data"""
        errors = {}
        
        if not self.copyright_agreed or not self.privacy_agreed:
            errors['agreements'] = "Both copyright and privacy agreements are required"
        
        # Validate keywords
        if self.keywords:
            keywords = [k.strip() for k in self.keywords.split(',')]
            if len(keywords) < 4:
                errors['keywords'] = "At least 4 keywords are required"
            elif len(keywords) > 6:
                errors['keywords'] = "Maximum 6 keywords allowed"
        
        # Validate abstract word count
        word_count = len(self.abstract.split())
        if word_count < 150 or word_count > 200:
            errors['abstract'] = f"Abstract must be 150-200 words (currently {word_count})"
        
        if errors:
            raise ValidationError(errors)


# ============================================================================
# SUBMISSION FILE MODEL - File uploads
# ============================================================================

class SubmissionFile(models.Model):
    """
    Represents uploaded manuscript files for a submission.
    Supports multiple files per submission.
    """
    
    FILE_TYPE_CHOICES = [
        ('pdf', 'PDF'),
        ('doc', 'Microsoft Word'),
        ('docx', 'Microsoft Word (DOCX)'),
        ('rtf', 'Rich Text Format'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    submission = models.ForeignKey(
        Submission,
        on_delete=models.CASCADE,
        related_name='files',
        help_text="Associated submission"
    )
    
    # File Details
    file = models.FileField(
        upload_to='submissions/%Y/%m/%d/',
        validators=[
            FileExtensionValidator(
                allowed_extensions=['pdf', 'doc', 'docx', 'rtf'],
                message='Only PDF, DOC, DOCX, and RTF files are allowed'
            )
        ],
        help_text="Manuscript file"
    )
    file_name = models.CharField(
        max_length=255,
        help_text="Original filename"
    )
    file_type = models.CharField(
        max_length=10,
        choices=FILE_TYPE_CHOICES,
        help_text="File type (auto-detected)"
    )
    file_size = models.BigIntegerField(
        help_text="File size in bytes"
    )
    
    # Metadata
    uploaded_at = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-uploaded_at']
        verbose_name = 'Submission File'
        verbose_name_plural = 'Submission Files'
        indexes = [
            models.Index(fields=['submission']),
            models.Index(fields=['file_type']),
        ]
    
    def __str__(self):
        return f"{self.file_name} ({self.get_file_type_display()})"
    
    def save(self, *args, **kwargs):
        """Set file metadata before saving"""
        if self.file:
            # Set filename
            self.file_name = os.path.basename(self.file.name)
            
            # Set file size
            self.file_size = self.file.size
            
            # Validate file size (max 100MB)
            if self.file_size > 100 * 1024 * 1024:
                raise ValidationError("File size must not exceed 100MB")
            
            # Detect file type
            ext = os.path.splitext(self.file_name)[1].lower().lstrip('.')
            if ext == 'pdf':
                self.file_type = 'pdf'
            elif ext == 'doc':
                self.file_type = 'doc'
            elif ext == 'docx':
                self.file_type = 'docx'
            elif ext == 'rtf':
                self.file_type = 'rtf'
        
        super().save(*args, **kwargs)
    
    def get_file_extension(self):
        """Get file extension"""
        return os.path.splitext(self.file_name)[1].lower()
    
    def get_file_size_mb(self):
        """Get file size in MB"""
        return round(self.file_size / (1024 * 1024), 2)


# ============================================================================
# REVIEWER MODEL - Peer review tracking
# ============================================================================

class Reviewer(models.Model):
    """
    Represents peer review assignments and tracking.
    Links reviewers to submissions with status and timelines.
    """
    
    STATUS_CHOICES = [
        ('invited', 'Invited'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed'),
        ('pending', 'Pending Response'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    submission = models.ForeignKey(
        Submission,
        on_delete=models.CASCADE,
        related_name='reviews',
        help_text="Associated submission"
    )
    author = models.ForeignKey(
        Author,
        on_delete=models.PROTECT,
        related_name='reviews',
        help_text="Reviewer"
    )
    
    # Review Details
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        help_text="Review status"
    )
    comments = models.TextField(
        blank=True,
        null=True,
        help_text="Reviewer comments"
    )
    rating = models.IntegerField(
        null=True,
        blank=True,
        choices=[(i, f"{i} - {['Poor', 'Fair', 'Good', 'Very Good', 'Excellent'][i-1]}") 
                 for i in range(1, 6)],
        help_text="Review rating (1-5)"
    )
    
    # Timeline
    invited_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When reviewer was invited"
    )
    due_date = models.DateField(
        null=True,
        blank=True,
        help_text="Review due date"
    )
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When review was completed"
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Reviewer'
        verbose_name_plural = 'Reviewers'
        unique_together = [['submission', 'author']]
        indexes = [
            models.Index(fields=['submission']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.author.full_name} - {self.submission.submission_number}"
    
    def is_overdue(self):
        """Check if review is overdue"""
        if self.due_date and not self.completed_at:
            return self.due_date < timezone.now().date()
        return False


# ============================================================================
# SUBMISSION LOG MODEL - Audit trail
# ============================================================================

class SubmissionLog(models.Model):
    """
    Audit trail for submission changes and actions.
    Immutable record of all events.
    """
    
    ACTION_CHOICES = [
        ('created', 'Submission Created'),
        ('updated', 'Submission Updated'),
        ('submitted', 'Submission Submitted'),
        ('status_changed', 'Status Changed'),
        ('file_added', 'File Added'),
        ('file_removed', 'File Removed'),
        ('reviewer_assigned', 'Reviewer Assigned'),
        ('review_completed', 'Review Completed'),
        ('email_sent', 'Email Sent'),
        ('comment_added', 'Comment Added'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    submission = models.ForeignKey(
        Submission,
        on_delete=models.CASCADE,
        related_name='logs',
        help_text="Associated submission"
    )
    
    # Log Details
    action = models.CharField(
        max_length=30,
        choices=ACTION_CHOICES,
        help_text="Action performed"
    )
    description = models.TextField(
        blank=True,
        null=True,
        help_text="Detailed description of action"
    )
    performed_by = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="User who performed the action"
    )
    
    # Metadata
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Submission Log'
        verbose_name_plural = 'Submission Logs'
        indexes = [
            models.Index(fields=['submission']),
            models.Index(fields=['action']),
            models.Index(fields=['-timestamp']),
        ]
    
    def __str__(self):
        return f"{self.submission.submission_number} - {self.get_action_display()}"
    
    # Make log immutable - prevent updates
    def save(self, *args, **kwargs):
        if self.pk:
            raise ValidationError("Submission logs cannot be modified")
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        raise ValidationError("Submission logs cannot be deleted")


# ============================================================================
# CONTACT MODEL - Contact form submissions (separate from articles)
# ============================================================================

class Contact(models.Model):
    """
    Represents contact form submissions from the website.
    Used for general inquiries, not article submissions.
    """
    
    SUBJECT_CHOICES = [
        ('paper_submission', 'Paper Submission'),
        ('general_inquiry', 'General Inquiry'),
        ('buy_journal', 'Buy Journal or Book'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Contact Details
    name = models.CharField(
        max_length=100,
        validators=[MinLengthValidator(3)],
        help_text="Full name"
    )
    email = models.EmailField(
        help_text="Email address"
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        help_text="Phone number (optional)"
    )
    subject = models.CharField(
        max_length=30,
        choices=SUBJECT_CHOICES,
        help_text="Inquiry subject"
    )
    message = models.TextField(
        validators=[MinLengthValidator(10)],
        help_text="Message content"
    )
    
    # Metadata
    is_read = models.BooleanField(
        default=False,
        help_text="Whether admin has read this message"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Contact'
        verbose_name_plural = 'Contacts'
        indexes = [
            models.Index(fields=['subject']),
            models.Index(fields=['is_read']),
            models.Index(fields=['-created_at']),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.get_subject_display()}"
