from django.db import models
from django.utils import timezone
from django.core.validators import EmailValidator
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid

class EmailTemplate(models.Model):
    """Reusable email templates"""
    
    EMAIL_TYPE_CHOICES = (
        ('SUBMISSION_CONFIRMATION', 'User Submission Confirmation'),
        ('ADMIN_NOTIFICATION', 'Admin New Submission Alert'),
        ('REVIEW_UPDATE', 'Review Status Update'),
        ('ACCEPTANCE', 'Paper Accepted'),
        ('REJECTION', 'Paper Rejected'),
        ('PAYMENT_REMINDER', 'Payment Reminder'),
        ('CONTACT_REPLY', 'Contact Form Reply'),
        ('WELCOME', 'Welcome Email'),
    )
    
    template_id = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
        db_index=True
    )
    name = models.CharField(
        max_length=100,
        unique=True,
        help_text="Template identifier (e.g., submission_confirmation)"
    )
    email_type = models.CharField(
        max_length=50,
        choices=EMAIL_TYPE_CHOICES,
        db_index=True
    )
    subject = models.CharField(
        max_length=200,
        help_text="Email subject with variables like {submission_id}, {author_name}"
    )
    body_html = models.TextField(
        help_text="HTML email body with variables"
    )
    body_text = models.TextField(
        help_text="Plain text fallback",
        null=True,
        blank=True
    )
    variables = models.JSONField(
        default=dict,
        help_text="Available template variables",
        blank=True
    )
    is_active = models.BooleanField(
        default=True,
        db_index=True
    )
    created_at = models.DateTimeField(
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        auto_now=True
    )
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['email_type', 'is_active']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.email_type})"
    
    def render(self, context):
        """Render template with context variables"""
        try:
            subject = self.subject.format(**context)
            body_html = self.body_html.format(**context)
            body_text = self.body_text.format(**context) if self.body_text else None
            return {
                'subject': subject,
                'body_html': body_html,
                'body_text': body_text
            }
        except KeyError as e:
            raise ValueError(f"Missing template variable: {e}")


class EmailLog(models.Model):
    """Track all email activities"""
    
    EMAIL_STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('SENT', 'Sent Successfully'),
        ('FAILED', 'Failed'),
        ('BOUNCED', 'Bounced'),
        ('OPENED', 'Opened'),
        ('CLICKED', 'Clicked'),
        ('RETRYING', 'Retrying'),
    )
    
    email_id = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
        db_index=True
    )
    recipient_email = models.EmailField(
        db_index=True,
        validators=[EmailValidator()]
    )
    sender_email = models.EmailField(
        default='noreply@istpublications.com'
    )
    subject = models.CharField(
        max_length=200
    )
    email_type = models.CharField(
        max_length=50,
        db_index=True
    )
    submission_id = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        db_index=True
    )
    status = models.CharField(
        max_length=20,
        choices=EMAIL_STATUS_CHOICES,
        default='PENDING',
        db_index=True
    )
    sent_at = models.DateTimeField(
        null=True,
        blank=True
    )
    failed_reason = models.TextField(
        null=True,
        blank=True,
        help_text="Error message if email failed"
    )
    read_count = models.IntegerField(
        default=0,
        help_text="Number of times email was opened"
    )
    retry_count = models.IntegerField(
        default=0,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(5),
    ]
    )
    template_used = models.ForeignKey(
        EmailTemplate,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True
    )
    updated_at = models.DateTimeField(
        auto_now=True
    )
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['recipient_email', 'status']),
            models.Index(fields=['email_type', 'status']),
            models.Index(fields=['submission_id', 'status']),
        ]
    
    def __str__(self):
        return f"{self.email_type} to {self.recipient_email} ({self.status})"
    
    def mark_as_sent(self):
        """Mark email as successfully sent"""
        self.status = 'SENT'
        self.sent_at = timezone.now()
        self.save(update_fields=['status', 'sent_at', 'updated_at'])
    
    def mark_as_failed(self, reason):
        """Mark email as failed with reason"""
        self.status = 'FAILED'
        self.failed_reason = reason
        self.save(update_fields=['status', 'failed_reason', 'updated_at'])
    
    def increment_retry(self):
        """Increment retry count"""
        self.retry_count += 1
        self.status = 'RETRYING'
        self.save(update_fields=['retry_count', 'status', 'updated_at'])
    
    def mark_as_opened(self):
        """Track email open"""
        self.read_count += 1
        self.status = 'OPENED'
        self.save(update_fields=['read_count', 'status', 'updated_at'])
    
    @property
    def is_recent(self):
        """Check if email was sent within last 24 hours"""
        if not self.sent_at:
            return False
        delta = timezone.now() - self.sent_at
        return delta.total_seconds() < 86400
    
    @staticmethod
    def get_failed_emails():
        """Get all failed emails that need retry"""
        return EmailLog.objects.filter(
            status='FAILED',
            retry_count__lt=5
        ).order_by('created_at')
