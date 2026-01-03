from django.db import models
from django.core.validators import EmailValidator, URLValidator
from django.utils import timezone
import uuid

# ============================================================================
# MODEL 1: Submission (Core Record)
# ============================================================================
class Submission(models.Model):
    """
    Main submission record. One submission = One complete journal article.
    Each submission has a unique submission_id and progresses through 6 steps.
    """
    
    STEP_CHOICES = [
        (1, 'Start'),
        (2, 'Enter Metadata'),
        (3, 'Upload Submission'),
        (4, 'Suggestive Reviewers'),
        (5, 'Confirmation'),
        (6, 'Next Steps'),
    ]
    
    STATUS_CHOICES = [
        ('DRAFT', 'Draft (In Progress)'),
        ('SUBMITTED', 'Submitted (Completed)'),
    ]
    
    # Primary Fields
    submission_id = models.CharField(
        max_length=20,
        unique=True,
        db_index=True,
        help_text="Auto-generated unique ID (e.g., IST-2025-001)"
    )
    
    author_name = models.CharField(
        max_length=255,
        help_text="Full name of article author"
    )
    
    author_email = models.EmailField(
        db_index=True,
        help_text="Email for communication & status updates"
    )
    
    # Submission Progress
    current_step = models.IntegerField(
        choices=STEP_CHOICES,
        default=1,
        help_text="Current step (1-6) in submission process"
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='DRAFT',
        db_index=True,
        help_text="DRAFT = in progress, SUBMITTED = completed"
    )
    
    is_locked = models.BooleanField(
        default=False,
        help_text="True after Step 6 (prevents editing)"
    )
    
    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        help_text="When submission was created"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Last update time"
    )
    
    submitted_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When submitted (Step 6 completed)"
    )
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['submission_id']),
            models.Index(fields=['author_email']),
            models.Index(fields=['status']),
            models.Index(fields=['-created_at']),
        ]
        verbose_name = "Submission"
        verbose_name_plural = "Submissions"
    
    def __str__(self):
        return f"{self.submission_id} - {self.author_name}"
    
    def mark_as_submitted(self):
        """Lock submission and mark as submitted"""
        self.status = 'SUBMITTED'
        self.is_locked = True
        self.current_step = 6
        self.submitted_at = timezone.now()
        self.save()


# ============================================================================
# MODEL 2: SubmissionStep1 (Policies & Agreements)
# ============================================================================
class SubmissionStep1(models.Model):
    """
    Step 1: User reads guidelines and acknowledges policies.
    Stores agreement checkboxes only.
    """
    
    submission = models.OneToOneField(
        Submission,
        on_delete=models.CASCADE,
        related_name='step1',
        help_text="Link to main submission"
    )
    
    step1_comments = models.TextField(
        blank=True,
        null=True,
        help_text="Optional comments for the editor"
    )
    
    agrees_to_copyright = models.BooleanField(
        default=False,
        help_text="User agrees to copyright terms"
    )
    
    agrees_to_privacy = models.BooleanField(
        default=False,
        help_text="User agrees to privacy policy"
    )
    
    agrees_to_policies = models.BooleanField(
        default=False,
        help_text="User agrees to submission policies"
    )
    
    saved_at = models.DateTimeField(
        auto_now=True,
        help_text="When step 1 was saved"
    )
    
    class Meta:
        verbose_name = "Submission Step 1"
        verbose_name_plural = "Submission Steps 1"
    
    def __str__(self):
        return f"Step 1 - {self.submission.submission_id}"


# ============================================================================
# MODEL 3: SubmissionStep2 (Metadata)
# ============================================================================
class SubmissionStep2(models.Model):
    """
    Step 2: User enters article metadata.
    Stores title, abstract, keywords, and category.
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
    
    submission = models.OneToOneField(
        Submission,
        on_delete=models.CASCADE,
        related_name='step2',
        help_text="Link to main submission"
    )
    
    title = models.CharField(
        max_length=300,
        help_text="Article title (5-300 characters)"
    )
    
    abstract = models.TextField(
        help_text="Article abstract (150-200 words recommended)"
    )
    
    keywords = models.CharField(
        max_length=500,
        help_text="Keywords separated by commas (e.g., AI, Machine Learning, Neural Networks)"
    )
    
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        help_text="Article category"
    )
    
    saved_at = models.DateTimeField(
        auto_now=True,
        help_text="When step 2 was saved"
    )
    
    class Meta:
        verbose_name = "Submission Step 2"
        verbose_name_plural = "Submission Steps 2"
    
    def __str__(self):
        return f"Step 2 - {self.submission.submission_id}"


# ============================================================================
# MODEL 4: SubmissionStep3 (Files)
# ============================================================================
class SubmissionStep3(models.Model):
    """
    Step 3: User uploads files (PDF, DOCX, RTF).
    Stores file metadata. Binary files stored in Supabase Storage.
    """
    
    FILE_TYPE_CHOICES = [
        ('pdf', 'PDF Document'),
        ('docx', 'Word Document'),
        ('rtf', 'Rich Text Format'),
    ]
    
    submission = models.ForeignKey(
        Submission,
        on_delete=models.CASCADE,
        related_name='step3_files',
        help_text="Link to main submission"
    )
    
    file_name = models.CharField(
        max_length=255,
        help_text="Original file name"
    )
    
    file_size = models.IntegerField(
        help_text="File size in bytes"
    )
    
    file_type = models.CharField(
        max_length=10,
        choices=FILE_TYPE_CHOICES,
        help_text="PDF, DOCX, or RTF"
    )
    
    storage_path = models.CharField(
        max_length=500,
        help_text="Path in Supabase Storage (e.g., submissions/IST-001/file.pdf)"
    )
    
    uploaded_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When file was uploaded"
    )
    
    class Meta:
        verbose_name = "Submission File"
        verbose_name_plural = "Submission Files"
    
    def __str__(self):
        return f"{self.submission.submission_id} - {self.file_name}"


# ============================================================================
# MODEL 5: SubmissionStep4 (Reviewers)
# ============================================================================
class SubmissionStep4(models.Model):
    """
    Step 4: User suggests 1-2 reviewers.
    Stores reviewer details (name, email, affiliation).
    """
    
    PREFIX_CHOICES = [
        ('Dr', 'Dr.'),
        ('Prof', 'Prof.'),
        ('Mr', 'Mr.'),
        ('Ms', 'Ms.'),
    ]
    
    submission = models.ForeignKey(
        Submission,
        on_delete=models.CASCADE,
        related_name='step4_reviewers',
        help_text="Link to main submission"
    )
    
    reviewer_number = models.IntegerField(
        choices=[(1, 'Reviewer 1'), (2, 'Reviewer 2')],
        help_text="1 or 2"
    )
    
    reviewer_prefix = models.CharField(
        max_length=10,
        choices=PREFIX_CHOICES,
        help_text="Dr, Prof, Mr, or Ms"
    )
    
    reviewer_name = models.CharField(
        max_length=255,
        help_text="Full name of suggested reviewer"
    )
    
    reviewer_email = models.EmailField(
        validators=[EmailValidator()],
        help_text="Reviewer email address"
    )
    
    reviewer_department = models.CharField(
        max_length=200,
        help_text="Department/Institute of reviewer"
    )
    
    reviewer_affiliation = models.CharField(
        max_length=200,
        help_text="University/Organization of reviewer"
    )
    
    suggested_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When reviewer was suggested"
    )
    
    class Meta:
        verbose_name = "Suggested Reviewer"
        verbose_name_plural = "Suggested Reviewers"
        unique_together = ('submission', 'reviewer_number')
    
    def __str__(self):
        return f"{self.submission.submission_id} - Reviewer {self.reviewer_number}: {self.reviewer_name}"


# ============================================================================
# MODEL 6: SubmissionStep5 (Final Confirmation)
# ============================================================================
class SubmissionStep5(models.Model):
    """
    Step 5: User confirms final agreements before submission.
    This is the last step before Step 6 (finalize/submit).
    """
    
    submission = models.OneToOneField(
        Submission,
        on_delete=models.CASCADE,
        related_name='step5',
        help_text="Link to main submission"
    )
    
    final_agrees_copyright = models.BooleanField(
        default=False,
        help_text="Final copyright agreement"
    )
    
    final_agrees_privacy = models.BooleanField(
        default=False,
        help_text="Final privacy agreement"
    )
    
    confirms_submission = models.BooleanField(
        default=False,
        help_text="User confirms ready to submit"
    )
    
    confirmed_at = models.DateTimeField(
        auto_now=True,
        help_text="When step 5 was confirmed"
    )
    
    class Meta:
        verbose_name = "Submission Step 5"
        verbose_name_plural = "Submission Steps 5"
    
    def __str__(self):
        return f"Step 5 - {self.submission.submission_id}"


# ============================================================================
# HELPER FUNCTION: Generate Submission ID
# ============================================================================
def generate_submission_id():
    """
    Generate unique submission ID in format: IST-YYYY-NNN
    Example: IST-2025-001
    
    Year is current year, NNN is sequential number for that year.
    """
    from datetime import datetime
    
    current_year = datetime.now().year
    
    # Count existing submissions for this year
    count = Submission.objects.filter(
        created_at__year=current_year
    ).count()
    
    # Generate ID with zero padding (001, 002, etc.)
    new_count = count + 1
    submission_id = f"IST-{current_year}-{new_count:03d}"
    
    return submission_id
