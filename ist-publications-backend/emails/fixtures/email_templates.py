"""
Load email templates into database
Run: python manage.py shell < apps/emails/fixtures/email_templates.py
"""

from apps.emails.models import EmailTemplate

# Delete existing templates
EmailTemplate.objects.all().delete()

# 1. Submission Confirmation Template
EmailTemplate.objects.create(
    name='submission_confirmation',
    email_type='SUBMISSION_CONFIRMATION',
    subject='Paper Submission Confirmed - IST Publications #{submission_number}',
    body_html="""
    <html>
    <body style="font-family: Arial, sans-serif; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
            <h1 style="color: #003366;">Thank You for Your Submission!</h1>
            
            <p>Dear {author_name},</p>
            
            <p>We are pleased to confirm that your paper has been successfully submitted to IST Publications.</p>
            
            <div style="background-color: #f4f7f6; padding: 15px; border-left: 4px solid #00509E; margin: 20px 0;">
                <p><strong>Submission Number:</strong> {submission_number}</p>
                <p><strong>Article Title:</strong> {article_title}</p>
                <p><strong>Submission Date:</strong> {submission_date}</p>
            </div>
            
            <h3>What Happens Next?</h3>
            <ol>
                <li>Your paper will be reviewed by our editorial board</li>
                <li>Initial review: 5-7 business days</li>
                <li>You will receive updates via email</li>
                <li>Expected decision: 2-3 weeks</li>
            </ol>
            
            <p>You can track your submission status at:</p>
            <a href="{portal_url}" style="color: #00509E; font-weight: bold;">View Your Submission</a>
            
            <h3>Need Help?</h3>
            <p>If you have any questions, please contact us at:</p>
            <p>Email: {support_email}</p>
            <p>Phone: +91-XXXX-XXXX-XX</p>
            
            <hr style="margin: 30px 0; border: none; border-top: 1px solid #ddd;">
            
            <p style="color: #666; font-size: 12px;">
                This is an automated email. Please do not reply directly to this email.
                Use the contact form on our website instead.
            </p>
        </div>
    </body>
    </html>
    """,
    body_text="""
    Thank You for Your Submission!
    
    Dear {author_name},
    
    We are pleased to confirm that your paper has been successfully submitted.
    
    Submission Number: {submission_number}
    Article Title: {article_title}
    Submission Date: {submission_date}
    
    What Happens Next?
    1. Your paper will be reviewed by our editorial board
    2. Initial review: 5-7 business days
    3. You will receive updates via email
    4. Expected decision: 2-3 weeks
    
    Track your submission at: {portal_url}
    
    Need Help?
    Email: {support_email}
    """,
    variables={
        'author_name': 'Name of the author',
        'submission_number': 'Unique submission identifier',
        'article_title': 'Title of the article',
        'submission_date': 'Date of submission',
        'portal_url': 'Link to submission portal',
        'support_email': 'Support email address'
    },
    is_active=True
)

# 2. Admin Notification Template
EmailTemplate.objects.create(
    name='admin_notification',
    email_type='ADMIN_NOTIFICATION',
    subject='New Paper Submission - {article_title} by {author_name}',
    body_html="""
    <html>
    <body style="font-family: Arial, sans-serif; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
            <h1 style="color: #003366;">New Paper Submission</h1>
            
            <div style="background-color: #f4f7f6; padding: 15px; border-left: 4px solid #00509E; margin: 20px 0;">
                <p><strong>Submission Number:</strong> {submission_number}</p>
                <p><strong>Author Name:</strong> {author_name}</p>
                <p><strong>Author Email:</strong> {author_email}</p>
                <p><strong>Article Title:</strong> {article_title}</p>
                <p><strong>Category:</strong> {category}</p>
                <p><strong>Submitted:</strong> {timestamp}</p>
            </div>
            
            <p><a href="{dashboard_url}" style="display: inline-block; background-color: #003366; color: white; padding: 10px 20px; text-decoration: none; border-radius: 4px; margin-top: 10px;">Review Submission</a></p>
            
            <h3>Quick Actions</h3>
            <ul>
                <li>Assign to reviewer</li>
                <li>Add to review queue</li>
                <li>Send status update</li>
            </ul>
        </div>
    </body>
    </html>
    """,
    body_text="""
    New Paper Submission
    
    Submission Number: {submission_number}
    Author: {author_name}
    Email: {author_email}
    Title: {article_title}
    Category: {category}
    Submitted: {timestamp}
    
    Review at: {dashboard_url}
    """,
    variables={
        'submission_number': 'Submission ID',
        'author_name': 'Author name',
        'author_email': 'Author email',
        'article_title': 'Article title',
        'category': 'Paper category',
        'timestamp': 'Submission time',
        'dashboard_url': 'Admin dashboard link'
    },
    is_active=True
)

# 3. Review Update Template
EmailTemplate.objects.create(
    name='review_update',
    email_type='REVIEW_UPDATE',
    subject='Paper Review Status Update - {article_title}',
    body_html="""
    <html>
    <body style="font-family: Arial, sans-serif; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
            <h1 style="color: #003366;">Review Status Update</h1>
            
            <p>Dear Author,</p>
            
            <p>We have an update on your submission:</p>
            
            <div style="background-color: #f4f7f6; padding: 15px; border-left: 4px solid #00509E; margin: 20px 0;">
                <p><strong>Submission:</strong> {submission_number}</p>
                <p><strong>Status:</strong> {review_status}</p>
            </div>
            
            <h3>Reviewer Feedback</h3>
            <p>{reviewer_comments}</p>
            
            <p><a href="{portal_url}" style="color: #00509E; font-weight: bold;">View Full Feedback</a></p>
        </div>
    </body>
    </html>
    """,
    body_text="""
    Review Status Update
    
    Submission: {submission_number}
    Status: {review_status}
    
    Reviewer Feedback:
    {reviewer_comments}
    
    View Full Feedback: {portal_url}
    """,
    variables={
        'submission_number': 'Submission ID',
        'review_status': 'Current review status',
        'reviewer_comments': 'Comments from reviewers',
        'portal_url': 'Link to view full feedback'
    },
    is_active=True
)

# 4. Acceptance Template
EmailTemplate.objects.create(
    name='acceptance',
    email_type='ACCEPTANCE',
    subject='Congratulations! Your Paper Has Been Accepted - {article_title}',
    body_html="""
    <html>
    <body style="font-family: Arial, sans-serif; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
            <h1 style="color: #28a745;">🎉 Congratulations!</h1>
            
            <p>Dear {author_name},</p>
            
            <p style="font-size: 16px; font-weight: bold; color: #28a745;">We are pleased to inform you that your paper has been accepted for publication!</p>
            
            <div style="background-color: #d4edda; padding: 15px; border-left: 4px solid #28a745; margin: 20px 0;">
                <p><strong>Submission Number:</strong> {submission_number}</p>
                <p><strong>Article Title:</strong> {article_title}</p>
            </div>
            
            <h3>Next Steps</h3>
            <ol>
                <li>Sign and return copyright transfer form</li>
                <li>Pay publication fee (if applicable)</li>
                <li>Receive proofs for final review</li>
                <li>Paper published in next issue</li>
            </ol>
            
            <p><a href="{next_steps_url}" style="display: inline-block; background-color: #28a745; color: white; padding: 10px 20px; text-decoration: none; border-radius: 4px; margin-top: 10px;">View Next Steps</a></p>
            
            <p>If you have any questions, please contact us at {support_email}</p>
        </div>
    </body>
    </html>
    """,
    body_text="""
    Congratulations!
    
    Dear {author_name},
    
    We are pleased to inform you that your paper has been accepted for publication!
    
    Submission Number: {submission_number}
    Article Title: {article_title}
    
    Next Steps:
    1. Sign and return copyright transfer form
    2. Pay publication fee (if applicable)
    3. Receive proofs for final review
    4. Paper published in next issue
    
    View Next Steps: {next_steps_url}
    """,
    variables={
        'author_name': 'Author name',
        'submission_number': 'Submission ID',
        'article_title': 'Article title',
        'congratulations_message': 'Congratulation message',
        'next_steps_url': 'Link to next steps',
        'support_email': 'Support email'
    },
    is_active=True
)

# 5. Rejection Template
EmailTemplate.objects.create(
    name='rejection',
    email_type='REJECTION',
    subject='Decision on Your Submission - {article_title}',
    body_html="""
    <html>
    <body style="font-family: Arial, sans-serif; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
            <h1 style="color: #003366;">Submission Decision</h1>
            
            <p>Dear {author_name},</p>
            
            <p>Thank you for submitting your paper to IST Publications.</p>
            
            <div style="background-color: #fff3cd; padding: 15px; border-left: 4px solid #ffc107; margin: 20px 0;">
                <p><strong>Article Title:</strong> {article_title}</p>
                <p><strong>Submission Number:</strong> {submission_number}</p>
                <p><strong>Decision:</strong> Not Accepted</p>
            </div>
            
            <h3>Feedback</h3>
            <p>{rejection_reason}</p>
            
            <h3>Next Steps</h3>
            <p>{resubmit_info}</p>
            
            <p>If you have questions about this decision, please contact us at {support_email}</p>
        </div>
    </body>
    </html>
    """,
    body_text="""
    Submission Decision
    
    Dear {author_name},
    
    Article Title: {article_title}
    Submission Number: {submission_number}
    Decision: Not Accepted
    
    Feedback:
    {rejection_reason}
    
    {resubmit_info}
    """,
    variables={
        'author_name': 'Author name',
        'submission_number': 'Submission ID',
        'article_title': 'Article title',
        'rejection_reason': 'Reason for rejection',
        'resubmit_info': 'Resubmission information',
        'support_email': 'Support email'
    },
    is_active=True
)

# 6. Contact Reply Template
EmailTemplate.objects.create(
    name='contact_reply',
    email_type='CONTACT_REPLY',
    subject='Re: {subject_line} - IST Publications',
    body_html="""
    <html>
    <body style="font-family: Arial, sans-serif; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
            <h1 style="color: #003366;">Response to Your Inquiry</h1>
            
            <p>Dear {name},</p>
            
            <p>Thank you for contacting IST Publications. We appreciate your interest.</p>
            
            <div style="background-color: #f4f7f6; padding: 15px; border-left: 4px solid #00509E; margin: 20px 0;">
                <p>{reply_message}</p>
            </div>
            
            <p>If you have further questions, please don't hesitate to contact us.</p>
            
            <p>Best regards,<br>IST Publications Team</p>
        </div>
    </body>
    </html>
    """,
    body_text="""
    Response to Your Inquiry
    
    Dear {name},
    
    Thank you for contacting IST Publications.
    
    {reply_message}
    
    Best regards,
    IST Publications Team
    """,
    variables={
        'name': 'User name',
        'subject_line': 'Original subject',
        'reply_message': 'Response message',
        'support_email': 'Support email'
    },
    is_active=True
)

print("✅ All email templates loaded successfully!")
