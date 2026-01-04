"""
Email statistics and monitoring views
"""

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.db.models import Count, Q
from datetime import datetime, timedelta
from .models import EmailLog, EmailTemplate
from .services import email_service
import json


@staff_member_required
def email_dashboard(request):
    """Email monitoring dashboard for admins"""
    
    # Get statistics
    stats = email_service.get_email_statistics()
    
    # Email type distribution
    email_types = EmailLog.objects.values('email_type').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Status distribution
    status_dist = EmailLog.objects.values('status').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Last 7 days trend
    last_7_days = datetime.now() - timedelta(days=7)
    daily_stats = []
    for i in range(7):
        date = last_7_days + timedelta(days=i)
        sent = EmailLog.objects.filter(
            status='SENT',
            created_at__date=date
        ).count()
        failed = EmailLog.objects.filter(
            status='FAILED',
            created_at__date=date
        ).count()
        daily_stats.append({
            'date': date.strftime('%Y-%m-%d'),
            'sent': sent,
            'failed': failed
        })
    
    # Failed emails
    failed_emails = EmailLog.objects.filter(status='FAILED').order_by('-created_at')[:10]
    
    context = {
        'stats': stats,
        'email_types': email_types,
        'status_dist': status_dist,
        'daily_stats': json.dumps(daily_stats),
        'failed_emails': failed_emails,
        'email_templates': EmailTemplate.objects.filter(is_active=True)
    }
    
    return render(request, 'emails/dashboard.html', context)


@staff_member_required
def email_statistics_api(request):
    """API endpoint for email statistics (JSON)"""
    
    stats = email_service.get_email_statistics()
    
    recent_emails = EmailLog.objects.filter(
        created_at__gte=datetime.now() - timedelta(days=7)
    ).values('email_type').annotate(count=Count('id'))
    
    return JsonResponse({
        'stats': stats,
        'recent_by_type': list(recent_emails),
        'timestamp': datetime.now().isoformat()
    })
