from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.views.decorators.http import require_http_methods
from .models import ContactMessage
from .serializers import ContactMessageSerializer
import logging

# Set up logging
logger = logging.getLogger(__name__)

@api_view(['POST'])
@permission_classes([AllowAny])
def contact_form_submit(request):
    """
    API endpoint to handle contact form submissions
    
    Expected POST data:
    {
        "name": "John Doe",
        "email": "john@example.com",
        "phone": "9876543210",
        "subject": "paper_submission",
        "message": "I want to submit a paper..."
    }
    
    Returns:
    - 201: Success - message saved to database
    - 400: Validation error - check field errors
    - 500: Server error
    """
    
    try:
        # Check if method is POST
        if request.method != 'POST':
            return Response(
                {'error': 'Only POST method allowed'},
                status=status.HTTP_405_METHOD_NOT_ALLOWED
            )
        
        # Get form data from request
        data = request.data
        
        # Validate using serializer
        serializer = ContactMessageSerializer(data=data)
        
        if serializer.is_valid():
            # Save to database
            contact_message = serializer.save()
            
            # Log success
            logger.info(f"Contact form submitted by {contact_message.name} ({contact_message.email})")
            
            # Return success response
            return Response(
                {
                    'success': True,
                    'message': 'Your message has been received. We will get back to you soon!',
                    'data': {
                        'id': contact_message.id,
                        'name': contact_message.name,
                        'email': contact_message.email,
                    }
                },
                status=status.HTTP_201_CREATED
            )
        else:
            # Return validation errors
            logger.warning(f"Contact form validation failed: {serializer.errors}")
            return Response(
                {
                    'success': False,
                    'message': 'Please correct the errors below',
                    'errors': serializer.errors
                },
                status=status.HTTP_400_BAD_REQUEST
            )
    
    except Exception as e:
        # Log error
        logger.error(f"Error in contact form: {str(e)}")
        
        # Return error response
        return Response(
            {
                'success': False,
                'message': 'An error occurred. Please try again later.'
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """
    Simple endpoint to check if backend is running
    """
    return Response(
        {
            'status': 'ok',
            'message': 'IST Publications Backend is running'
        },
        status=status.HTTP_200_OK
    )
