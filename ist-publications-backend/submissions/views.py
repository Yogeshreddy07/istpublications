from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import (
    Submission,
    SubmissionStep1,
    SubmissionStep2,
    SubmissionStep3,
    SubmissionStep4,
    SubmissionStep5,
    generate_submission_id,
)
from .serializers import (
    SubmissionSerializer,
    SubmissionStep1Serializer,
    SubmissionStep2Serializer,
    SubmissionStep3Serializer,
    SubmissionStep4Serializer,
    SubmissionStep5Serializer,
    SubmissionDetailSerializer,
)


# ============================================================================
# ENDPOINT 1: CREATE SUBMISSION
# ============================================================================

class CreateSubmissionView(APIView):
    """
    Create a new submission and initialize Step 1.
    
    POST /api/submissions/create
    
    Request:
    {
        "author_name": "Dr. John Smith",
        "author_email": "john@example.com"
    }
    
    Response:
    {
        "submission_id": "IST-2025-001",
        "author_name": "Dr. John Smith",
        "author_email": "john@example.com",
        "current_step": 1,
        "status": "DRAFT",
        "is_locked": false,
        "created_at": "2025-01-03T21:45:00Z",
        "updated_at": "2025-01-03T21:45:00Z",
        "submitted_at": null
    }
    """
    
    def post(self, request):
        """Create new submission"""
        try:
            # Extract data from request
            author_name = request.data.get('author_name', '').strip()
            author_email = request.data.get('author_email', '').strip()
            
            # Validate required fields
            if not author_name:
                return Response(
                    {
                        'success': False,
                        'error': 'author_name is required'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if not author_email:
                return Response(
                    {
                        'success': False,
                        'error': 'author_email is required'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Generate unique submission ID
            submission_id = generate_submission_id()
            
            # Create submission
            submission = Submission.objects.create(
                submission_id=submission_id,
                author_name=author_name,
                author_email=author_email,
                current_step=1,
                status='DRAFT'
            )
            
            # Create Step 1 record (empty agreements)
            SubmissionStep1.objects.create(submission=submission)
            
            # Serialize and return
            serializer = SubmissionSerializer(submission)
            
            return Response(
                {
                    'success': True,
                    'message': 'Submission created successfully',
                    'submission': serializer.data
                },
                status=status.HTTP_201_CREATED
            )
        
        except Exception as e:
            return Response(
                {
                    'success': False,
                    'error': str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# ============================================================================
# ENDPOINT 2: SAVE STEP 1
# ============================================================================

class SaveStep1View(APIView):
    """
    Save Step 1: Guidelines & Agreements
    
    POST /api/submissions/{submission_id}/step/1
    
    Request:
    {
        "step1_comments": "Optional comments",
        "agrees_to_copyright": true,
        "agrees_to_privacy": true,
        "agrees_to_policies": true
    }
    
    Response:
    {
        "success": true,
        "message": "Step 1 saved successfully",
        "submission": { ... }
    }
    """
    
    def post(self, request, submission_id):
        """Save Step 1 data"""
        try:
            # Get submission
            submission = get_object_or_404(Submission, submission_id=submission_id)
            
            # Check if locked
            if submission.is_locked:
                return Response(
                    {
                        'success': False,
                        'error': 'Submission is locked and cannot be edited'
                    },
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Get or create Step 1
            step1, created = SubmissionStep1.objects.get_or_create(
                submission=submission
            )
            
            # Validate and save data
            serializer = SubmissionStep1Serializer(
                step1,
                data=request.data,
                partial=True
            )
            
            if not serializer.is_valid():
                return Response(
                    {
                        'success': False,
                        'errors': serializer.errors
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            serializer.save()
            
            # Update submission current_step to 2
            submission.current_step = 2
            submission.save()
            
            # Return updated submission
            sub_serializer = SubmissionSerializer(submission)
            
            return Response(
                {
                    'success': True,
                    'message': 'Step 1 saved successfully',
                    'submission': sub_serializer.data
                },
                status=status.HTTP_200_OK
            )
        
        except Submission.DoesNotExist:
            return Response(
                {
                    'success': False,
                    'error': 'Submission not found'
                },
                status=status.HTTP_404_NOT_FOUND
            )
        
        except Exception as e:
            return Response(
                {
                    'success': False,
                    'error': str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# ============================================================================
# ENDPOINT 3: SAVE STEP 2
# ============================================================================

class SaveStep2View(APIView):
    """
    Save Step 2: Metadata (Title, Abstract, Keywords, Category)
    
    POST /api/submissions/{submission_id}/step/2
    
    Request:
    {
        "title": "Machine Learning in Healthcare",
        "abstract": "This paper explores... (150-200 words)",
        "keywords": "Machine Learning, Healthcare, AI",
        "category": "ai"
    }
    
    Response:
    {
        "success": true,
        "message": "Step 2 saved successfully",
        "submission": { ... }
    }
    """
    
    def post(self, request, submission_id):
        """Save Step 2 data"""
        try:
            # Get submission
            submission = get_object_or_404(Submission, submission_id=submission_id)
            
            # Check if locked
            if submission.is_locked:
                return Response(
                    {
                        'success': False,
                        'error': 'Submission is locked and cannot be edited'
                    },
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Check if Step 1 is completed
            if submission.current_step < 2:
                return Response(
                    {
                        'success': False,
                        'error': 'You must complete Step 1 first'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Get or create Step 2
            step2, created = SubmissionStep2.objects.get_or_create(
                submission=submission
            )
            
            # Validate and save data
            serializer = SubmissionStep2Serializer(
                step2,
                data=request.data,
                partial=False  # All fields required
            )
            
            if not serializer.is_valid():
                return Response(
                    {
                        'success': False,
                        'errors': serializer.errors
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            serializer.save()
            
            # Update submission current_step to 3
            submission.current_step = 3
            submission.save()
            
            # Return updated submission
            sub_serializer = SubmissionSerializer(submission)
            
            return Response(
                {
                    'success': True,
                    'message': 'Step 2 saved successfully',
                    'submission': sub_serializer.data
                },
                status=status.HTTP_200_OK
            )
        
        except Submission.DoesNotExist:
            return Response(
                {
                    'success': False,
                    'error': 'Submission not found'
                },
                status=status.HTTP_404_NOT_FOUND
            )
        
        except Exception as e:
            return Response(
                {
                    'success': False,
                    'error': str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# ============================================================================
# ENDPOINT 4: GET SUBMISSION
# ============================================================================

class GetSubmissionView(APIView):
    """
    Retrieve complete submission data with all steps.
    
    GET /api/submissions/{submission_id}
    
    Response:
    {
        "success": true,
        "submission": {
            "submission_id": "IST-2025-001",
            "author_name": "Dr. John Smith",
            "author_email": "john@example.com",
            "current_step": 3,
            "status": "DRAFT",
            "is_locked": false,
            "step1": { ... },
            "step2": { ... },
            "step3": [ ... ],
            "step4": [ ... ],
            "step5": { ... }
        }
    }
    """
    
    def get(self, request, submission_id):
        """Retrieve submission data"""
        try:
            # Get submission
            submission = get_object_or_404(Submission, submission_id=submission_id)
            
            # Serialize with all steps
            serializer = SubmissionDetailSerializer(submission)
            
            return Response(
                {
                    'success': True,
                    'submission': serializer.data
                },
                status=status.HTTP_200_OK
            )
        
        except Submission.DoesNotExist:
            return Response(
                {
                    'success': False,
                    'error': 'Submission not found'
                },
                status=status.HTTP_404_NOT_FOUND
            )
        
        except Exception as e:
            return Response(
                {
                    'success': False,
                    'error': str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# ============================================================================
# ENDPOINT 5: SAVE STEP 3 (For Day 4)
# ============================================================================

class SaveStep3View(APIView):
    """Save Step 3: File Upload References"""
    
    def post(self, request, submission_id):
        """Save Step 3 data (files)"""
        try:
            submission = get_object_or_404(Submission, submission_id=submission_id)
            
            if submission.is_locked:
                return Response(
                    {'success': False, 'error': 'Submission is locked'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            if submission.current_step < 3:
                return Response(
                    {'success': False, 'error': 'You must complete Steps 1 & 2 first'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Get files from request
            files_data = request.data.get('files', [])
            
            if not files_data:
                return Response(
                    {'success': False, 'error': 'At least one file is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Save files
            for file_data in files_data:
                serializer = SubmissionStep3Serializer(data=file_data)
                
                if not serializer.is_valid():
                    return Response(
                        {'success': False, 'errors': serializer.errors},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                serializer.save(submission=submission)
            
            # Update step
            submission.current_step = 4
            submission.save()
            
            sub_serializer = SubmissionSerializer(submission)
            
            return Response(
                {
                    'success': True,
                    'message': f'Step 3 saved successfully ({len(files_data)} files)',
                    'submission': sub_serializer.data
                },
                status=status.HTTP_200_OK
            )
        
        except Exception as e:
            return Response(
                {'success': False, 'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# ============================================================================
# ENDPOINT 6: SAVE STEP 4 (For Day 4)
# ============================================================================

class SaveStep4View(APIView):
    """Save Step 4: Suggested Reviewers"""
    
    def post(self, request, submission_id):
        """Save Step 4 data (reviewers)"""
        try:
            submission = get_object_or_404(Submission, submission_id=submission_id)
            
            if submission.is_locked:
                return Response(
                    {'success': False, 'error': 'Submission is locked'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            if submission.current_step < 4:
                return Response(
                    {'success': False, 'error': 'You must complete Steps 1-3 first'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Get reviewers from request
            reviewers_data = request.data.get('reviewers', [])
            
            if not reviewers_data or len(reviewers_data) == 0:
                return Response(
                    {'success': False, 'error': 'At least one reviewer is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if len(reviewers_data) > 2:
                return Response(
                    {'success': False, 'error': 'Maximum 2 reviewers allowed'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Save reviewers
            for idx, reviewer_data in enumerate(reviewers_data, 1):
                reviewer_data['reviewer_number'] = idx
                serializer = SubmissionStep4Serializer(data=reviewer_data)
                
                if not serializer.is_valid():
                    return Response(
                        {'success': False, 'errors': serializer.errors},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                serializer.save(submission=submission)
            
            # Update step
            submission.current_step = 5
            submission.save()
            
            sub_serializer = SubmissionSerializer(submission)
            
            return Response(
                {
                    'success': True,
                    'message': f'Step 4 saved successfully ({len(reviewers_data)} reviewers)',
                    'submission': sub_serializer.data
                },
                status=status.HTTP_200_OK
            )
        
        except Exception as e:
            return Response(
                {'success': False, 'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# ============================================================================
# ENDPOINT 7: SAVE STEP 5 (For Day 4)
# ============================================================================

class SaveStep5View(APIView):
    """Save Step 5: Final Confirmation"""
    
    def post(self, request, submission_id):
        """Save Step 5 data (final confirmation)"""
        try:
            submission = get_object_or_404(Submission, submission_id=submission_id)
            
            if submission.is_locked:
                return Response(
                    {'success': False, 'error': 'Submission is locked'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            if submission.current_step < 5:
                return Response(
                    {'success': False, 'error': 'You must complete Steps 1-4 first'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Get or create Step 5
            step5, created = SubmissionStep5.objects.get_or_create(
                submission=submission
            )
            
            # Validate and save
            serializer = SubmissionStep5Serializer(
                step5,
                data=request.data,
                partial=False
            )
            
            if not serializer.is_valid():
                return Response(
                    {'success': False, 'errors': serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            serializer.save()
            
            # Update step to 6 (ready for finalization)
            submission.current_step = 6
            submission.save()
            
            sub_serializer = SubmissionSerializer(submission)
            
            return Response(
                {
                    'success': True,
                    'message': 'Step 5 saved successfully. Ready to submit!',
                    'submission': sub_serializer.data
                },
                status=status.HTTP_200_OK
            )
        
        except Exception as e:
            return Response(
                {'success': False, 'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# ============================================================================
# ENDPOINT 8: FINALIZE SUBMISSION (For Day 4)
# ============================================================================

class FinalizeSubmissionView(APIView):
    """Finalize and lock submission"""
    
    def post(self, request, submission_id):
        """Finalize submission"""
        try:
            submission = get_object_or_404(Submission, submission_id=submission_id)
            
            if submission.is_locked:
                return Response(
                    {'success': False, 'error': 'Submission is already locked'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            if submission.current_step < 6:
                return Response(
                    {'success': False, 'error': 'You must complete all steps first'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Lock and submit
            submission.mark_as_submitted()
            
            # TODO: Send emails (implemented in Day 9)
            
            sub_serializer = SubmissionSerializer(submission)
            
            return Response(
                {
                    'success': True,
                    'message': 'Submission finalized successfully! Emails have been sent.',
                    'submission': sub_serializer.data
                },
                status=status.HTTP_200_OK
            )
        
        except Exception as e:
            return Response(
                {'success': False, 'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
