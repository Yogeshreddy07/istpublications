# Phase 3: URL Configuration
# File: submissions/urls.py
# Complete API endpoints configuration

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .views import (
    AuthorViewSet,
    SubmissionViewSet,
    SubmissionFileViewSet,
    ContactViewSet,
    FormSubmissionView,
)

# Create router
router = DefaultRouter()
router.register(r'authors', AuthorViewSet, basename='author')
router.register(r'submissions', SubmissionViewSet, basename='submission')
router.register(r'files', SubmissionFileViewSet, basename='submission-file')
router.register(r'contact', ContactViewSet, basename='contact')

# Health check endpoint
class HealthCheckView(APIView):
    def get(self, request):
        return Response({
            'status': 'ok',
            'message': 'IST Publications API is running'
        })

# API endpoints
urlpatterns = [
    # Standard CRUD endpoints
    path('', include(router.urls)),
    
    # Form submission endpoint (complete 6-step form)
    path('submit-article/', FormSubmissionView.as_view({'post': 'create'}), 
         name='submit-article'),
    
    # Health check
    path('health/', HealthCheckView.as_view(), name='health-check'),
]


# ============================================================================
# PROJECT LEVEL URL CONFIGURATION
# ============================================================================
# Add this to your main urls.py (project/urls.py):
#
# from django.contrib import admin
# from django.urls import path, include
# from django.conf import settings
# from django.conf.urls.static import static
#
# urlpatterns = [
#     path('admin/', admin.site.urls),
#     path('api/', include('submissions.urls')),
# ]
#
# if settings.DEBUG:
#     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
#
# ============================================================================
