# Phase 3: REST API Views
# File: submissions/views.py
# Complete API endpoints for form submission and management

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import get_object_or_404
from django.db import transaction
from .models import (
    Author, Submission, SubmissionFile, 
    Reviewer, SubmissionLog, Contact
)
from .serializers import (
    AuthorSerializer,
    SubmissionSerializer,
    SubmissionFileSerializer,
    ReviewerSerializer,
    ContactSerializer,
    FormSubmissionSerializer,
)


# ============================================================================
# AUTHOR VIEWSET
# ============================================================================

class AuthorViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing authors
    
    GET /api/authors/
    POST /api/authors/
    GET /api/authors/{id}/
    PUT /api/authors/{id}/
    DELETE /api/authors/{id}/
    """
    
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    
    def get_queryset(self):
        """Filter by role if provided"""
        queryset = Author.objects.all()
        role = self.request.query_params.get('role')
        if role:
            queryset = queryset.filter(role=role)
        return queryset


# ============================================================================
# SUBMISSION VIEWSET
# ============================================================================

class SubmissionViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing submissions
    
    GET /api/submissions/
    POST /api/submissions/
    GET /api/submissions/{id}/
    PUT /api/submissions/{id}/
    DELETE /api/submissions/{id}/
    POST /api/submissions/{id}/submit/
    POST /api/submissions/{id}/mark-under-review/
    """
    
    queryset = Submission.objects.all()
    serializer_class = SubmissionSerializer
    parser_classes = (MultiPartParser, FormParser)
    
    def get_queryset(self):
        """Filter submissions by status if provided"""
        queryset = Submission.objects.all().select_related(
            'main_author', 'reviewer_1', 'reviewer_2'
        ).prefetch_related('co_authors', 'files', 'logs')
        
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        category_filter = self.request.query_params.get('category')
        if category_filter:
            queryset = queryset.filter(category=category_filter)
        
        return queryset
    
    @action(detail=True, methods=['post'])
    @transaction.atomic
    def submit(self, request, pk=None):
        """
        Submit a draft submission (change status to 'submitted')
        POST /api/submissions/{id}/submit/
        """
        submission = self.get_object()
        
        if submission.status != 'draft':
            return Response(
                {'error': 'Only draft submissions can be submitted'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate required fields
        if not submission.copyright_agreed or not submission.privacy_agreed:
            return Response(
                {'error': 'Both agreements must be accepted'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not submission.files.exists():
            return Response(
                {'error': 'At least one file must be uploaded'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Update submission
        submission.status = 'submitted'
        from django.utils import timezone
        submission.submitted_at = timezone.now()
        submission.save()
        
        # Log action
        SubmissionLog.objects.create(
            submission=submission,
            action='submitted',
            description='Submission finalized and sent for review',
            performed_by=request.user.username if request.user.is_authenticated else 'Anonymous'
        )
        
        serializer = self.get_serializer(submission)
        return Response({
            'message': 'Submission successful',
            'submission_number': submission.submission_number,
            'data': serializer.data
        }, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'])
    def mark_under_review(self, request, pk=None):
        """
        Mark submission as under review
        POST /api/submissions/{id}/mark-under-review/
        """
        submission = self.get_object()
        submission.status = 'under_review'
        submission.save()
        
        SubmissionLog.objects.create(
            submission=submission,
            action='status_changed',
            description='Status changed to Under Review',
            performed_by=request.user.username
        )
        
        serializer = self.get_serializer(submission)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def mark_accepted(self, request, pk=None):
        """
        Mark submission as accepted
        POST /api/submissions/{id}/mark-accepted/
        """
        submission = self.get_object()
        submission.status = 'accepted'
        submission.save()
        
        SubmissionLog.objects.create(
            submission=submission,
            action='status_changed',
            description='Status changed to Accepted',
            performed_by=request.user.username
        )
        
        serializer = self.get_serializer(submission)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def mark_rejected(self, request, pk=None):
        """
        Mark submission as rejected
        POST /api/submissions/{id}/mark-rejected/
        """
        submission = self.get_object()
        submission.status = 'rejected'
        submission.save()
        
        SubmissionLog.objects.create(
            submission=submission,
            action='status_changed',
            description='Status changed to Rejected',
            performed_by=request.user.username
        )
        
        serializer = self.get_serializer(submission)
        return Response(serializer.data)


# ============================================================================
# SUBMISSION FILE VIEWSET
# ============================================================================

class SubmissionFileViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing submission files
    
    GET /api/files/
    POST /api/files/
    GET /api/files/{id}/
    DELETE /api/files/{id}/
    """
    
    queryset = SubmissionFile.objects.all()
    serializer_class = SubmissionFileSerializer
    parser_classes = (MultiPartParser, FormParser)
    
    @action(detail=False, methods=['post'])
    @transaction.atomic
    def upload(self, request):
        """
        Upload file to submission
        POST /api/files/upload/
        
        Required: submission_id, file
        """
        submission_id = request.data.get('submission_id')
        if not submission_id:
            return Response(
                {'error': 'submission_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        submission = get_object_or_404(Submission, id=submission_id)
        
        file = request.FILES.get('file')
        if not file:
            return Response(
                {'error': 'file is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create file record
        submission_file = SubmissionFile.objects.create(
            submission=submission,
            file=file
        )
        
        # Log action
        SubmissionLog.objects.create(
            submission=submission,
            action='file_added',
            description=f'File uploaded: {submission_file.file_name}',
            performed_by=request.user.username if request.user.is_authenticated else 'Anonymous'
        )
        
        serializer = self.get_serializer(submission_file)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


# ============================================================================
# FORM SUBMISSION ENDPOINT (MAIN)
# ============================================================================

class FormSubmissionView(viewsets.ViewSet):
    """
    Complete form submission endpoint
    Handles all 6 steps of submit.html form
    
    POST /api/submit-article/
    """
    
    @transaction.atomic
    def create(self, request):
        """
        Submit complete form with all data
        
        Expected data structure:
        {
            "step1_comments": "...",
            "corresponding_contact": true,
            "copyright_agreed": true,
            "privacy_agreed": true,
            
            "main_author": {
                "full_name": "Dr. John Doe",
                "email": "john@example.com",
                "affiliation": "MIT"
            },
            "co_authors": [...],
            "title": "...",
            "abstract": "...",
            "keywords": "...",
            "category": "ai",
            
            "files": [...],
            
            "reviewer_1": {...},
            "reviewer_2": {...}
        }
        """
        serializer = FormSubmissionSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            submission = serializer.save()
            
            # Update status to submitted
            submission.status = 'submitted'
            from django.utils import timezone
            submission.submitted_at = timezone.now()
            submission.save()
            
            # Log submission
            SubmissionLog.objects.create(
                submission=submission,
                action='submitted',
                description='Article submitted via web form',
                performed_by=request.user.username if request.user.is_authenticated else 'Anonymous'
            )
            
            # Return success response
            response_serializer = SubmissionSerializer(submission)
            return Response({
                'message': 'Article submitted successfully',
                'submission_number': submission.submission_number,
                'status': 'submitted',
                'submission': response_serializer.data
            }, status=status.HTTP_201_CREATED)
        
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


# ============================================================================
# CONTACT FORM ENDPOINT
# ============================================================================

class ContactViewSet(viewsets.ModelViewSet):
    """
    API endpoint for contact form
    
    GET /api/contact/
    POST /api/contact/
    GET /api/contact/{id}/
    """
    
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer
    
    def create(self, request, *args, **kwargs):
        """Create contact form submission"""
        serializer = self.get_serializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer.save()
        
        return Response({
            'message': 'Contact form submitted successfully. We will reply within 24 hours.',
            'data': serializer.data
        }, status=status.HTTP_201_CREATED)
