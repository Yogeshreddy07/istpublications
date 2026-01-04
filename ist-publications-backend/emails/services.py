import logging
import smtplib
from typing import Dict, Optional, List
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import timezone
from django.conf import settings
import os

from .models import EmailLog, EmailTemplate

logger = logging.getLogger(__name__)


class EmailService:
    """Core email service for handling all email operations"""
    
    def __init__(self):
        self.sender_email = settings.DEFAULT_FROM_EMAIL
        self.admin_email = os.getenv('ADMIN_EMAIL', 'admin@istpublications.com')
    
    def get_template(self, template_type: str) -> Optional[EmailTemplate]:
        """Get active email template by type"""
        try:
            return EmailTemplate.objects.get(
                email_type=template_type,
                is_active=True
            )
        except EmailTemplate.DoesNotExist:
            logger.error(f"Email template not found: {template_type}")
            return None
    
    def render_template(
        self,
        template: EmailTemplate,
        context: Dict
    ) -> Dict[str, str]:
        """Render template with context"""
        try:
            return template.render(context)
        except ValueError as e:
            logger.error(f"Template rendering error: {e}")
            raise
    
    def send_email(
        self,
        recipient: str,
        subject: str,
        body_html: str,
        body_text: Optional[str] = None,
        email_type: str = 'GENERAL',
        submission_id: Optional[str] = None,
        template: Optional[EmailTemplate] = None
    ) -> EmailLog:
        """
        Send email and log activity
        
        Args:
            recipient: Email address
            subject: Email subject
            body_html: HTML body
            body_text: Plain text fallback
            email_type: Type of email
            submission_id: Associated submission ID
            template: Template object used
        
        Returns:
            EmailLog object
        """
        
        # Create email log entry
        email_log = EmailLog.objects.create(
            recipient_email=recipient,
            sender_email=self.sender_email,
            subject=subject,
            email_type=email_type,
            submission_id=submission_id,
            template_used=template,
            status='PENDING'
        )
        
        try:
            # Create email
            email = EmailMultiAlternatives(
                subject=subject,
                body=body_text or body_html,
                from_email=self.sender_email,
                to=[recipient]
            )
            
            # Add HTML alternative
            email.attach_alternative(body_html, "text/html")
            
            # Send email
            email.send(fail_silently=False)
            
            # Mark as sent
            email_log.mark_as_sent()
            logger.info(f"Email sent to {recipient} - ID: {email_log.email_id}")
            
            return email_log
        
        except smtplib.SMTPException as e:
            error_msg = f"SMTP Error: {str(e)}"
            email_log.mark_as_failed(error_msg)
            logger.error(error_msg)
            return email_log
        
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            email_log.mark_as_failed(error_msg)
            logger.error(error_msg)
            return email_log
    
    def send_submission_confirmation(
        self,
        recipient: str,
        submission_number: str,
        article_title: str,
        author_name: str,
        submission_date: str
    ) -> EmailLog:
        """Send submission confirmation to user"""
        
        template = self.get_template('SUBMISSION_CONFIRMATION')
        if not template:
            raise ValueError("Submission confirmation template not found")
        
        context = {
            'author_name': author_name,
            'submission_number': submission_number,
            'article_title': article_title,
            'submission_date': submission_date,
            'portal_url': f"{settings.FRONTEND_URL}/submission/{submission_number}",
            'support_email': self.admin_email
        }
        
        rendered = self.render_template(template, context)
        
        return self.send_email(
            recipient=recipient,
            subject=rendered['subject'],
            body_html=rendered['body_html'],
            body_text=rendered['body_text'],
            email_type='SUBMISSION_CONFIRMATION',
            submission_id=submission_number,
            template=template
        )
    
    def send_admin_notification(
        self,
        submission_number: str,
        article_title: str,
        author_name: str,
        author_email: str,
        category: str
    ) -> EmailLog:
        """Send notification to admin about new submission"""
        
        template = self.get_template('ADMIN_NOTIFICATION')
        if not template:
            raise ValueError("Admin notification template not found")
        
        context = {
            'submission_number': submission_number,
            'article_title': article_title,
            'author_name': author_name,
            'author_email': author_email,
            'category': category,
            'dashboard_url': f"{settings.BACKEND_URL}/admin/submissions/{submission_number}",
            'timestamp': timezone.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        rendered = self.render_template(template, context)
        
        return self.send_email(
            recipient=self.admin_email,
            subject=rendered['subject'],
            body_html=rendered['body_html'],
            body_text=rendered['body_text'],
            email_type='ADMIN_NOTIFICATION',
            submission_id=submission_number,
            template=template
        )
    
    def send_review_update(
        self,
        recipient: str,
        submission_number: str,
        article_title: str,
        review_status: str,
        reviewer_comments: Optional[str] = None
    ) -> EmailLog:
        """Send review status update"""
        
        template = self.get_template('REVIEW_UPDATE')
        if not template:
            raise ValueError("Review update template not found")
        
        context = {
            'submission_number': submission_number,
            'article_title': article_title,
            'review_status': review_status,
            'reviewer_comments': reviewer_comments or 'N/A',
            'portal_url': f"{settings.FRONTEND_URL}/submission/{submission_number}",
            'support_email': self.admin_email
        }
        
        rendered = self.render_template(template, context)
        
        return self.send_email(
            recipient=recipient,
            subject=rendered['subject'],
            body_html=rendered['body_html'],
            body_text=rendered['body_text'],
            email_type='REVIEW_UPDATE',
            submission_id=submission_number,
            template=template
        )
    
    def send_acceptance_email(
        self,
        recipient: str,
        submission_number: str,
        article_title: str,
        author_name: str
    ) -> EmailLog:
        """Send acceptance notification"""
        
        template = self.get_template('ACCEPTANCE')
        if not template:
            raise ValueError("Acceptance template not found")
        
        context = {
            'author_name': author_name,
            'submission_number': submission_number,
            'article_title': article_title,
            'congratulations_message': 'We are pleased to inform you that your paper has been accepted!',
            'next_steps_url': f"{settings.FRONTEND_URL}/accepted/{submission_number}",
            'support_email': self.admin_email
        }
        
        rendered = self.render_template(template, context)
        
        return self.send_email(
            recipient=recipient,
            subject=rendered['subject'],
            body_html=rendered['body_html'],
            body_text=rendered['body_text'],
            email_type='ACCEPTANCE',
            submission_id=submission_number,
            template=template
        )
    
    def send_rejection_email(
        self,
        recipient: str,
        submission_number: str,
        article_title: str,
        author_name: str,
        rejection_reason: Optional[str] = None
    ) -> EmailLog:
        """Send rejection notification"""
        
        template = self.get_template('REJECTION')
        if not template:
            raise ValueError("Rejection template not found")
        
        context = {
            'author_name': author_name,
            'submission_number': submission_number,
            'article_title': article_title,
            'rejection_reason': rejection_reason or 'Does not meet our current criteria',
            'resubmit_info': 'You are welcome to resubmit an improved version in the future.',
            'support_email': self.admin_email
        }
        
        rendered = self.render_template(template, context)
        
        return self.send_email(
            recipient=recipient,
            subject=rendered['subject'],
            body_html=rendered['body_html'],
            body_text=rendered['body_text'],
            email_type='REJECTION',
            submission_id=submission_number,
            template=template
        )
    
    def send_contact_reply(
        self,
        recipient: str,
        name: str,
        subject_line: str,
        reply_message: str
    ) -> EmailLog:
        """Send reply to contact form inquiry"""
        
        template = self.get_template('CONTACT_REPLY')
        if not template:
            raise ValueError("Contact reply template not found")
        
        context = {
            'name': name,
            'subject_line': subject_line,
            'reply_message': reply_message,
            'support_email': self.admin_email,
            'contact_url': f"{settings.FRONTEND_URL}/contact"
        }
        
        rendered = self.render_template(template, context)
        
        return self.send_email(
            recipient=recipient,
            subject=rendered['subject'],
            body_html=rendered['body_html'],
            body_text=rendered['body_text'],
            email_type='CONTACT_REPLY'
        )
    
    def retry_failed_emails(self, max_retries=5):
        """Retry all failed emails (max 5 times)"""
        
        failed_emails = EmailLog.get_failed_emails()
        retried_count = 0
        
        for email_log in failed_emails:
            if email_log.retry_count >= max_retries:
                logger.warning(f"Max retries reached for email: {email_log.email_id}")
                continue
            
            try:
                email_log.increment_retry()
                # Retry sending
                # (Implementation depends on storing original email data)
                logger.info(f"Retrying email: {email_log.email_id}")
                retried_count += 1
            except Exception as e:
                logger.error(f"Error retrying email {email_log.email_id}: {e}")
        
        return retried_count
    
    def get_email_statistics(self):
        """Get email sending statistics"""
        
        stats = {
            'total_sent': EmailLog.objects.filter(status='SENT').count(),
            'total_failed': EmailLog.objects.filter(status='FAILED').count(),
            'total_pending': EmailLog.objects.filter(status='PENDING').count(),
            'today_sent': EmailLog.objects.filter(
                status='SENT',
                created_at__date=timezone.now().date()
            ).count(),
            'failure_rate': self._calculate_failure_rate(),
        }
        
        return stats
    
    def _calculate_failure_rate(self) -> float:
        """Calculate email failure rate"""
        total = EmailLog.objects.filter(
            status__in=['SENT', 'FAILED']
        ).count()
        
        if total == 0:
            return 0.0
        
        failed = EmailLog.objects.filter(status='FAILED').count()
        return (failed / total) * 100


# Singleton instance
email_service = EmailService()
