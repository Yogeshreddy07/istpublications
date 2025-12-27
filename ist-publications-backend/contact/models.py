from django.db import models
from django.core.validators import EmailValidator
from django.utils import timezone

class ContactMessage(models.Model):
    """
    Model to store contact form submissions from the frontend
    """
    
    # Subject choices
    SUBJECT_CHOICES = [
        ('paper_submission', 'Paper Submission'),
        ('general_inquiry', 'General Inquiry'),
        ('buy_journal', 'Buy Journal or Book'),
    ]
    
    # Fields
    name = models.CharField(
        max_length=255,
        help_text="Full name of the person"
    )
    email = models.EmailField(
        validators=[EmailValidator()],
        help_text="Valid email address"
    )
    phone = models.CharField(
        max_length=20,
        help_text="Contact phone number"
    )
    subject = models.CharField(
        max_length=50,
        choices=SUBJECT_CHOICES,
        help_text="Reason for contacting"
    )
    message = models.TextField(
        help_text="Message content"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Status (optional - for future use)
    is_read = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']  # Newest first
        verbose_name = "Contact Message"
        verbose_name_plural = "Contact Messages"
    
    def __str__(self):
        return f"{self.name} - {self.subject} ({self.created_at.date()})"
