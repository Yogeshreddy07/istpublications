from rest_framework import serializers
from django.utils import timezone
from .models import (
    Submission,
    SubmissionStep1,
    SubmissionStep2,
    SubmissionStep3,
    SubmissionStep4,
    SubmissionStep5,
)
import re


# ============================================================================
# CUSTOM VALIDATORS
# ============================================================================

class WordCountValidator:
    """Validates that text has between min and max words"""
    
    def __init__(self, min_words=150, max_words=200):
        self.min_words = min_words
        self.max_words = max_words
    
    def __call__(self, value):
        """Count words in text"""
        if not value:
            raise serializers.ValidationError("Text cannot be empty")
        
        word_count = len(value.split())
        
        if word_count < self.min_words:
            raise serializers.ValidationError(
                f"Abstract must have at least {self.min_words} words. "
                f"Current: {word_count} words"
            )
        
        if word_count > self.max_words:
            raise serializers.ValidationError(
                f"Abstract must have at most {self.max_words} words. "
                f"Current: {word_count} words"
            )


class EmailFormatValidator:
    """Validates email format"""
    
    def __call__(self, value):
        """Validate email"""
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        if not re.match(email_regex, value):
            raise serializers.ValidationError(
                f"Invalid email format: {value}"
            )


class KeywordValidator:
    """Validates keywords"""
    
    def __call__(self, value):
        """Validate keywords"""
        if not value or value.strip() == '':
            raise serializers.ValidationError("Keywords cannot be empty")
        
        keywords = [k.strip() for k in value.split(',') if k.strip()]
        
        if len(keywords) < 2:
            raise serializers.ValidationError(
                "At least 2 keywords are required (comma-separated)"
            )
        
        if len(keywords) > 10:
            raise serializers.ValidationError(
                "Maximum 10 keywords allowed"
            )


# ============================================================================
# SERIALIZER 1: SubmissionStep1Serializer
# ============================================================================

class SubmissionStep1Serializer(serializers.ModelSerializer):
    """
    Serializer for Step 1: Guidelines & Agreements
    Validates that user agrees to all policies
    """
    
    class Meta:
        model = SubmissionStep1
        fields = [
            'step1_comments',
            'agrees_to_copyright',
            'agrees_to_privacy',
            'agrees_to_policies',
        ]
    
    def validate_agrees_to_copyright(self, value):
        """Copyright agreement must be true"""
        if not value:
            raise serializers.ValidationError(
                "You must agree to copyright terms to proceed"
            )
        return value
    
    def validate_agrees_to_privacy(self, value):
        """Privacy agreement must be true"""
        if not value:
            raise serializers.ValidationError(
                "You must agree to privacy policy to proceed"
            )
        return value
    
    def validate_agrees_to_policies(self, value):
        """Policy agreement must be true"""
        if not value:
            raise serializers.ValidationError(
                "You must agree to submission policies to proceed"
            )
        return value


# ============================================================================
# SERIALIZER 2: SubmissionStep2Serializer
# ============================================================================

class SubmissionStep2Serializer(serializers.ModelSerializer):
    """
    Serializer for Step 2: Metadata (Title, Abstract, Keywords, Category)
    Validates all fields with strict rules
    """
    
    class Meta:
        model = SubmissionStep2
        fields = [
            'title',
            'abstract',
            'keywords',
            'category',
        ]
    
    def validate_title(self, value):
        """
        Validate title:
        - Min 5 characters
        - Max 300 characters
        - No HTML tags
        """
        if not value or value.strip() == '':
            raise serializers.ValidationError("Title cannot be empty")
        
        value = value.strip()
        
        if len(value) < 5:
            raise serializers.ValidationError(
                f"Title must be at least 5 characters. Current: {len(value)}"
            )
        
        if len(value) > 300:
            raise serializers.ValidationError(
                f"Title must be at most 300 characters. Current: {len(value)}"
            )
        
        # Check for HTML tags
        if re.search(r'<[^>]+>', value):
            raise serializers.ValidationError(
                "Title cannot contain HTML tags"
            )
        
        return value
    
    def validate_abstract(self, value):
        """
        Validate abstract:
        - 150-200 words
        - No HTML tags
        """
        if not value or value.strip() == '':
            raise serializers.ValidationError("Abstract cannot be empty")
        
        value = value.strip()
        
        # Check for HTML tags
        if re.search(r'<[^>]+>', value):
            raise serializers.ValidationError(
                "Abstract cannot contain HTML tags"
            )
        
        # Use custom validator
        validator = WordCountValidator(min_words=150, max_words=200)
        validator(value)
        
        return value
    
    def validate_keywords(self, value):
        """
        Validate keywords:
        - Comma-separated
        - Min 2, Max 10 keywords
        """
        if not value or value.strip() == '':
            raise serializers.ValidationError("Keywords cannot be empty")
        
        # Use custom validator
        validator = KeywordValidator()
        validator(value)
        
        return value
    
    def validate_category(self, value):
        """Category must be from valid choices"""
        valid_categories = [
            'ai', 'architecture', 'basic', 'biomedical', 'business',
            'cs', 'data', 'economics', 'engineering', 'management'
        ]
        
        if value not in valid_categories:
            raise serializers.ValidationError(
                f"Invalid category: {value}. "
                f"Must be one of: {', '.join(valid_categories)}"
            )
        
        return value


# ============================================================================
# SERIALIZER 3: SubmissionStep3Serializer
# ============================================================================

class SubmissionStep3Serializer(serializers.ModelSerializer):
    """
    Serializer for Step 3: File Upload References
    Validates file metadata (not binary)
    """
    
    class Meta:
        model = SubmissionStep3
        fields = [
            'file_name',
            'file_size',
            'file_type',
            'storage_path',
        ]
        read_only_fields = [
            'storage_path',
        ]
    
    def validate_file_name(self, value):
        """Validate file name"""
        if not value or value.strip() == '':
            raise serializers.ValidationError("File name cannot be empty")
        
        return value
    
    def validate_file_size(self, value):
        """
        Validate file size:
        - Max 10 MB (10485760 bytes)
        """
        max_size = 10 * 1024 * 1024  # 10 MB
        
        if value > max_size:
            size_mb = value / (1024 * 1024)
            raise serializers.ValidationError(
                f"File size ({size_mb:.2f} MB) exceeds maximum of 10 MB"
            )
        
        if value <= 0:
            raise serializers.ValidationError(
                "File size must be greater than 0"
            )
        
        return value
    
    def validate_file_type(self, value):
        """
        Validate file type:
        - Only PDF, DOCX, RTF allowed
        """
        valid_types = ['pdf', 'docx', 'rtf']
        
        if value not in valid_types:
            raise serializers.ValidationError(
                f"Invalid file type: {value}. "
                f"Allowed types: {', '.join(valid_types)}"
            )
        
        return value


# ============================================================================
# SERIALIZER 4: SubmissionStep4Serializer
# ============================================================================

class SubmissionStep4Serializer(serializers.ModelSerializer):
    """
    Serializer for Step 4: Suggested Reviewers
    Validates reviewer details
    """
    
    class Meta:
        model = SubmissionStep4
        fields = [
            'reviewer_number',
            'reviewer_prefix',
            'reviewer_name',
            'reviewer_email',
            'reviewer_department',
            'reviewer_affiliation',
        ]
    
    def validate_reviewer_prefix(self, value):
        """Validate reviewer prefix"""
        valid_prefixes = ['Dr', 'Prof', 'Mr', 'Ms']
        
        if value not in valid_prefixes:
            raise serializers.ValidationError(
                f"Invalid prefix: {value}. "
                f"Must be one of: {', '.join(valid_prefixes)}"
            )
        
        return value
    
    def validate_reviewer_name(self, value):
        """Validate reviewer name"""
        if not value or value.strip() == '':
            raise serializers.ValidationError("Reviewer name cannot be empty")
        
        if len(value) < 3:
            raise serializers.ValidationError(
                "Reviewer name must be at least 3 characters"
            )
        
        if len(value) > 255:
            raise serializers.ValidationError(
                "Reviewer name must be at most 255 characters"
            )
        
        return value.strip()
    
    def validate_reviewer_email(self, value):
        """Validate reviewer email"""
        if not value or value.strip() == '':
            raise serializers.ValidationError("Reviewer email cannot be empty")
        
        # Use custom validator
        validator = EmailFormatValidator()
        validator(value)
        
        return value.lower()
    
    def validate_reviewer_department(self, value):
        """Validate reviewer department"""
        if not value or value.strip() == '':
            raise serializers.ValidationError("Department cannot be empty")
        
        if len(value) > 200:
            raise serializers.ValidationError(
                "Department must be at most 200 characters"
            )
        
        return value.strip()
    
    def validate_reviewer_affiliation(self, value):
        """Validate reviewer affiliation"""
        if not value or value.strip() == '':
            raise serializers.ValidationError("Affiliation cannot be empty")
        
        if len(value) > 200:
            raise serializers.ValidationError(
                "Affiliation must be at most 200 characters"
            )
        
        return value.strip()


# ============================================================================
# SERIALIZER 5: SubmissionStep5Serializer
# ============================================================================

class SubmissionStep5Serializer(serializers.ModelSerializer):
    """
    Serializer for Step 5: Final Confirmation
    All agreements must be true before submission
    """
    
    class Meta:
        model = SubmissionStep5
        fields = [
            'final_agrees_copyright',
            'final_agrees_privacy',
            'confirms_submission',
        ]
    
    def validate_final_agrees_copyright(self, value):
        """Copyright agreement must be true"""
        if not value:
            raise serializers.ValidationError(
                "You must agree to copyright terms to submit"
            )
        return value
    
    def validate_final_agrees_privacy(self, value):
        """Privacy agreement must be true"""
        if not value:
            raise serializers.ValidationError(
                "You must agree to privacy policy to submit"
            )
        return value
    
    def validate_confirms_submission(self, value):
        """Submission confirmation must be true"""
        if not value:
            raise serializers.ValidationError(
                "You must confirm submission to proceed"
            )
        return value


# ============================================================================
# SERIALIZER 6: SubmissionSerializer (Main Record)
# ============================================================================

class SubmissionSerializer(serializers.ModelSerializer):
    """
    Serializer for Submission model
    Handles creation and updates
    """
    
    class Meta:
        model = Submission
        fields = [
            'submission_id',
            'author_name',
            'author_email',
            'current_step',
            'status',
            'is_locked',
            'created_at',
            'updated_at',
            'submitted_at',
        ]
        read_only_fields = [
            'submission_id',
            'created_at',
            'updated_at',
            'submitted_at',
        ]
    
    def validate_author_name(self, value):
        """Validate author name"""
        if not value or value.strip() == '':
            raise serializers.ValidationError("Author name cannot be empty")
        
        if len(value) < 3:
            raise serializers.ValidationError(
                "Author name must be at least 3 characters"
            )
        
        if len(value) > 255:
            raise serializers.ValidationError(
                "Author name must be at most 255 characters"
            )
        
        return value.strip()
    
    def validate_author_email(self, value):
        """Validate author email"""
        if not value or value.strip() == '':
            raise serializers.ValidationError("Author email cannot be empty")
        
        # Use custom validator
        validator = EmailFormatValidator()
        validator(value)
        
        return value.lower()
    
    def validate_current_step(self, value):
        """Validate step number"""
        if value not in [1, 2, 3, 4, 5, 6]:
            raise serializers.ValidationError(
                "Step must be between 1 and 6"
            )
        
        return value
    
    def validate_status(self, value):
        """Validate status"""
        valid_statuses = ['DRAFT', 'SUBMITTED']
        
        if value not in valid_statuses:
            raise serializers.ValidationError(
                f"Invalid status: {value}. "
                f"Must be one of: {', '.join(valid_statuses)}"
            )
        
        return value


# ============================================================================
# NESTED SERIALIZER: Complete Submission with all Steps
# ============================================================================

class SubmissionDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for complete submission with all steps
    Used in GET requests to return full submission data
    """
    
    step1 = SubmissionStep1Serializer(read_only=True)
    step2 = SubmissionStep2Serializer(read_only=True)
    step3 = SubmissionStep3Serializer(many=True, read_only=True, source='step3_files')
    step4 = SubmissionStep4Serializer(many=True, read_only=True, source='step4_reviewers')
    step5 = SubmissionStep5Serializer(read_only=True)
    
    class Meta:
        model = Submission
        fields = [
            'submission_id',
            'author_name',
            'author_email',
            'current_step',
            'status',
            'is_locked',
            'created_at',
            'updated_at',
            'submitted_at',
            'step1',
            'step2',
            'step3',
            'step4',
            'step5',
        ]
        read_only_fields = fields


# ============================================================================
# ADMIN SERIALIZER: For Admin Dashboard
# ============================================================================

class SubmissionListSerializer(serializers.ModelSerializer):
    """
    Minimal serializer for admin dashboard listing
    Shows only essential fields for table view
    """
    
    file_count = serializers.SerializerMethodField()
    reviewer_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Submission
        fields = [
            'submission_id',
            'author_name',
            'author_email',
            'title',
            'category',
            'current_step',
            'status',
            'file_count',
            'reviewer_count',
            'created_at',
            'submitted_at',
        ]
    
    def get_file_count(self, obj):
        """Count files for submission"""
        return obj.step3_files.count()
    
    def get_title(self, obj):
        """Get title from Step 2"""
        if hasattr(obj, 'step2') and obj.step2:
            return obj.step2.title
        return "N/A"
    
    def get_category(self, obj):
        """Get category from Step 2"""
        if hasattr(obj, 'step2') and obj.step2:
            return obj.step2.category
        return "N/A"
    
    def get_reviewer_count(self, obj):
        """Count reviewers for submission"""
        return obj.step4_reviewers.count()
