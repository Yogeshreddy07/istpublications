# Phase 3: REST API Endpoints for Form Submission
# File: submissions/serializers.py
# Complete serializers for all models with validation

from rest_framework import serializers
from django.core.exceptions import ValidationError
from .models import Author, Submission, SubmissionFile, Reviewer, SubmissionLog, Contact


# ============================================================================
# AUTHOR SERIALIZER
# ============================================================================

class AuthorSerializer(serializers.ModelSerializer):
    """Serializer for Author model"""
    
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    
    class Meta:
        model = Author
        fields = [
            'id',
            'full_name',
            'email',
            'affiliation',
            'department',
            'role',
            'role_display',
            'title',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'role_display']
    
    def validate_full_name(self, value):
        """Validate author name"""
        if len(value.strip()) < 3:
            raise serializers.ValidationError("Author name must be at least 3 characters long")
        return value.strip()
    
    def validate_affiliation(self, value):
        """Validate affiliation"""
        if len(value.strip()) < 5:
            raise serializers.ValidationError("Affiliation must be at least 5 characters long")
        return value.strip()


# ============================================================================
# SUBMISSION FILE SERIALIZER
# ============================================================================

class SubmissionFileSerializer(serializers.ModelSerializer):
    """Serializer for uploaded files"""
    
    file_type_display = serializers.CharField(source='get_file_type_display', read_only=True)
    file_size_mb = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = SubmissionFile
        fields = [
            'id',
            'file',
            'file_name',
            'file_type',
            'file_type_display',
            'file_size',
            'file_size_mb',
            'uploaded_at',
        ]
        read_only_fields = [
            'id',
            'file_name',
            'file_type',
            'file_size',
            'file_size_mb',
            'uploaded_at',
        ]
    
    def get_file_size_mb(self, obj):
        """Get file size in MB"""
        return round(obj.file_size / (1024 * 1024), 2)


# ============================================================================
# REVIEWER SERIALIZER
# ============================================================================

class ReviewerSerializer(serializers.ModelSerializer):
    """Serializer for Reviewer model"""
    
    author_name = serializers.CharField(source='author.full_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Reviewer
        fields = [
            'id',
            'submission',
            'author',
            'author_name',
            'status',
            'status_display',
            'comments',
            'rating',
            'invited_at',
            'due_date',
            'completed_at',
        ]
        read_only_fields = [
            'id',
            'author_name',
            'status_display',
            'created_at',
            'updated_at',
        ]


# ============================================================================
# SUBMISSION SERIALIZER (MAIN)
# ============================================================================

class SubmissionSerializer(serializers.ModelSerializer):
    """Main serializer for Submission model"""
    
    main_author = AuthorSerializer(read_only=True)
    main_author_id = serializers.UUIDField(write_only=True, source='main_author.id')
    
    co_authors = AuthorSerializer(many=True, read_only=True)
    co_author_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Author.objects.all(),
        write_only=True,
        required=False,
        source='co_authors'
    )
    
    files = SubmissionFileSerializer(many=True, read_only=True)
    
    reviewer_1 = AuthorSerializer(read_only=True)
    reviewer_1_id = serializers.UUIDField(write_only=True, required=False, allow_null=True)
    
    reviewer_2 = AuthorSerializer(read_only=True, required=False)
    reviewer_2_id = serializers.UUIDField(write_only=True, required=False, allow_null=True)
    
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    
    class Meta:
        model = Submission
        fields = [
            'id',
            'submission_number',
            'status',
            'status_display',
            'title',
            'abstract',
            'keywords',
            'category',
            'category_display',
            'main_author',
            'main_author_id',
            'co_authors',
            'co_author_ids',
            'reviewer_1',
            'reviewer_1_id',
            'reviewer_2',
            'reviewer_2_id',
            'files',
            'corresponding_contact',
            'copyright_agreed',
            'privacy_agreed',
            'editor_comments',
            'submitted_at',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'submission_number',
            'status',
            'status_display',
            'category_display',
            'main_author',
            'co_authors',
            'reviewer_1',
            'reviewer_2',
            'files',
            'submitted_at',
            'created_at',
            'updated_at',
        ]
    
    def validate_title(self, value):
        """Validate title"""
        if len(value) < 10 or len(value) > 300:
            raise serializers.ValidationError("Title must be 10-300 characters long")
        return value
    
    def validate_abstract(self, value):
        """Validate abstract"""
        word_count = len(value.split())
        if word_count < 150:
            raise serializers.ValidationError("Abstract must be at least 150 words")
        if word_count > 300:
            raise serializers.ValidationError("Abstract should not exceed 300 words")
        return value
    
    def validate_keywords(self, value):
        """Validate keywords"""
        if not value:
            raise serializers.ValidationError("Keywords are required")
        
        keywords = [k.strip() for k in value.split(',')]
        if len(keywords) < 4:
            raise serializers.ValidationError("At least 4 keywords are required")
        if len(keywords) > 6:
            raise serializers.ValidationError("Maximum 6 keywords allowed")
        
        return value
    
    def validate(self, data):
        """Validate overall submission"""
        if not data.get('copyright_agreed'):
            raise serializers.ValidationError("Copyright agreement is required")
        
        if not data.get('privacy_agreed'):
            raise serializers.ValidationError("Privacy agreement is required")
        
        return data
    
    def create(self, validated_data):
        """Create submission with related objects"""
        # Extract related objects data
        main_author_id = validated_data.pop('main_author', {}).get('id') or self.initial_data.get('main_author_id')
        co_author_ids = validated_data.pop('co_authors', [])
        reviewer_1_id = self.initial_data.get('reviewer_1_id')
        reviewer_2_id = self.initial_data.get('reviewer_2_id')
        
        # Get authors
        try:
            main_author = Author.objects.get(id=main_author_id)
        except Author.DoesNotExist:
            raise serializers.ValidationError("Main author not found")
        
        # Create submission
        submission = Submission.objects.create(
            main_author=main_author,
            **validated_data
        )
        
        # Add co-authors
        if co_author_ids:
            submission.co_authors.set(co_author_ids[:4])  # Max 4
        
        # Set reviewers
        if reviewer_1_id:
            try:
                submission.reviewer_1 = Author.objects.get(id=reviewer_1_id)
            except Author.DoesNotExist:
                pass
        
        if reviewer_2_id:
            try:
                submission.reviewer_2 = Author.objects.get(id=reviewer_2_id)
            except Author.DoesNotExist:
                pass
        
        submission.save()
        
        return submission


# ============================================================================
# CONTACT SERIALIZER
# ============================================================================

class ContactSerializer(serializers.ModelSerializer):
    """Serializer for Contact form"""
    
    subject_display = serializers.CharField(source='get_subject_display', read_only=True)
    
    class Meta:
        model = Contact
        fields = [
            'id',
            'name',
            'email',
            'phone',
            'subject',
            'subject_display',
            'message',
            'is_read',
            'created_at',
        ]
        read_only_fields = ['id', 'subject_display', 'is_read', 'created_at']
    
    def validate_message(self, value):
        """Validate message"""
        if len(value.strip()) < 10:
            raise serializers.ValidationError("Message must be at least 10 characters long")
        return value.strip()


# ============================================================================
# FORM SUBMISSION SERIALIZER (STEP-BY-STEP)
# ============================================================================

class FormSubmissionSerializer(serializers.Serializer):
    """
    Complete form submission serializer
    Handles all 6 steps of the submission form from submit.html
    """
    
    # STEP 1: Policies & Acceptance
    step1_comments = serializers.CharField(required=False, allow_blank=True)
    corresponding_contact = serializers.BooleanField(default=False)
    copyright_agreed = serializers.BooleanField(required=True)
    privacy_agreed = serializers.BooleanField(required=True)
    
    # STEP 2: Authors & Metadata
    main_author = AuthorSerializer()
    co_authors = AuthorSerializer(many=True, required=False, allow_empty=True)
    title = serializers.CharField(max_length=300)
    abstract = serializers.CharField()
    keywords = serializers.CharField()
    category = serializers.ChoiceField(choices=['ai', 'architecture', 'basic', 'biomedical', 
                                                 'business', 'cs', 'data', 'economics', 
                                                 'engineering', 'management'])
    
    # STEP 3: Files
    files = serializers.ListField(
        child=serializers.FileField(),
        required=False,
        allow_empty=True
    )
    
    # STEP 4: Reviewers
    reviewer_1 = AuthorSerializer()
    reviewer_2 = AuthorSerializer(required=False, allow_null=True)
    
    def validate_copyright_agreed(self, value):
        if not value:
            raise serializers.ValidationError("Copyright agreement is required")
        return value
    
    def validate_privacy_agreed(self, value):
        if not value:
            raise serializers.ValidationError("Privacy agreement is required")
        return value
    
    def validate_title(self, value):
        if len(value) < 10 or len(value) > 300:
            raise serializers.ValidationError("Title must be 10-300 characters long")
        return value
    
    def validate_abstract(self, value):
        word_count = len(value.split())
        if word_count < 150:
            raise serializers.ValidationError("Abstract must be at least 150 words")
        return value
    
    def validate_keywords(self, value):
        keywords = [k.strip() for k in value.split(',')]
        if len(keywords) < 4 or len(keywords) > 6:
            raise serializers.ValidationError("4-6 keywords required")
        return value
    
    def validate_co_authors(self, value):
        if len(value) > 4:
            raise serializers.ValidationError("Maximum 4 co-authors allowed")
        return value
    
    def validate_files(self, value):
        if not value:
            raise serializers.ValidationError("At least one file is required")
        
        for file in value:
            # Check extension
            allowed = ['pdf', 'doc', 'docx', 'rtf']
            ext = file.name.split('.')[-1].lower()
            if ext not in allowed:
                raise serializers.ValidationError(f"File type {ext} not allowed")
            
            # Check size (100MB)
            if file.size > 100 * 1024 * 1024:
                raise serializers.ValidationError("File size must not exceed 100MB")
        
        return value
    
    def create(self, validated_data):
        """Create submission from form data"""
        # Create main author
        main_author_data = validated_data.pop('main_author')
        main_author, _ = Author.objects.get_or_create(
            email=main_author_data['email'],
            defaults={
                'full_name': main_author_data['full_name'],
                'affiliation': main_author_data['affiliation'],
                'role': 'author'
            }
        )
        
        # Create co-authors
        co_authors = []
        for co_author_data in validated_data.pop('co_authors', []):
            author, _ = Author.objects.get_or_create(
                email=co_author_data['email'],
                defaults={
                    'full_name': co_author_data['full_name'],
                    'affiliation': co_author_data['affiliation'],
                    'role': 'co-author'
                }
            )
            co_authors.append(author)
        
        # Create reviewers
        reviewer_1_data = validated_data.pop('reviewer_1', None)
        reviewer_2_data = validated_data.pop('reviewer_2', None)
        
        reviewer_1 = None
        if reviewer_1_data:
            reviewer_1, _ = Author.objects.get_or_create(
                email=reviewer_1_data['email'],
                defaults={
                    'full_name': reviewer_1_data['full_name'],
                    'affiliation': reviewer_1_data['affiliation'],
                    'department': reviewer_1_data.get('department', ''),
                    'title': reviewer_1_data.get('title'),
                    'role': 'reviewer'
                }
            )
        
        reviewer_2 = None
        if reviewer_2_data:
            reviewer_2, _ = Author.objects.get_or_create(
                email=reviewer_2_data['email'],
                defaults={
                    'full_name': reviewer_2_data['full_name'],
                    'affiliation': reviewer_2_data['affiliation'],
                    'department': reviewer_2_data.get('department', ''),
                    'title': reviewer_2_data.get('title'),
                    'role': 'reviewer'
                }
            )
        
        # Handle files
        files = validated_data.pop('files', [])
        
        # Create submission
        submission = Submission.objects.create(
            main_author=main_author,
            reviewer_1=reviewer_1,
            reviewer_2=reviewer_2,
            editor_comments=validated_data.pop('step1_comments', ''),
            **validated_data
        )
        
        # Add co-authors
        for co_author in co_authors[:4]:
            submission.co_authors.add(co_author)
        
        # Create submission files
        for file in files:
            SubmissionFile.objects.create(
                submission=submission,
                file=file
            )
        
        # Log submission
        from .models import SubmissionLog
        log = SubmissionLog(
            submission=submission,
            action='submitted',
            description='Article submitted via web form'
        )
        log.save(force_insert=True)
        
        return submission
