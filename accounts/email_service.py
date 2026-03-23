"""
Email service for sending approval notifications
"""
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class ApprovalEmailService:
    """Service for sending approval-related emails"""
    
    @staticmethod
    def send_approval_email(user):
        """
        Send approval notification email to influencer
        
        Args:
            user: User object that was approved
        """
        try:
            subject = 'Your Account Has Been Approved! 🎉'
            
            # Email context
            context = {
                'user_name': user.username or user.first_name or 'Influencer',
                'login_url': f"{settings.FRONTEND_URL}/login",
                'dashboard_url': f"{settings.FRONTEND_URL}/dashboard",
                'support_email': settings.DEFAULT_FROM_EMAIL,
            }
            
            # Plain text message
            message = f"""
Hello {context['user_name']}!

Great news! Your influencer account has been approved and is now active.

You can now:
✓ Login to your dashboard
✓ Browse and apply for campaigns
✓ Connect with brands
✓ Start earning

Login here: {context['login_url']}

If you have any questions, feel free to reach out to our support team at {context['support_email']}.

Welcome to Collabo!

Best regards,
The Collabo Team
            """.strip()
            
            # HTML message (optional, for better formatting)
            html_message = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
        .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
        .button {{ display: inline-block; padding: 12px 30px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
        .features {{ background: white; padding: 20px; border-radius: 5px; margin: 20px 0; }}
        .feature {{ padding: 10px 0; }}
        .feature::before {{ content: "✓"; color: #667eea; font-weight: bold; margin-right: 10px; }}
        .footer {{ text-align: center; color: #666; font-size: 12px; margin-top: 30px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎉 Account Approved!</h1>
        </div>
        <div class="content">
            <p>Hello <strong>{context['user_name']}</strong>!</p>
            
            <p>Great news! Your influencer account has been approved and is now active.</p>
            
            <div class="features">
                <div class="feature">Login to your dashboard</div>
                <div class="feature">Browse and apply for campaigns</div>
                <div class="feature">Connect with brands</div>
                <div class="feature">Start earning</div>
            </div>
            
            <center>
                <a href="{context['login_url']}" class="button">Login to Dashboard</a>
            </center>
            
            <p>If you have any questions, feel free to reach out to our support team at <a href="mailto:{context['support_email']}">{context['support_email']}</a>.</p>
            
            <p><strong>Welcome to Collabo!</strong></p>
            
            <div class="footer">
                <p>Best regards,<br>The Collabo Team</p>
                <p>This is an automated message. Please do not reply to this email.</p>
            </div>
        </div>
    </div>
</body>
</html>
            """.strip()
            
            # Send email
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                html_message=html_message,
                fail_silently=False,
            )
            
            logger.info(f"Approval email sent successfully to {user.email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send approval email to {user.email}: {str(e)}")
            return False
    
    @staticmethod
    def send_rejection_email(user, reason=''):
        """
        Send rejection notification email to influencer
        
        Args:
            user: User object that was rejected
            reason: Reason for rejection
        """
        try:
            subject = 'Update on Your Account Application'
            
            context = {
                'user_name': user.username or user.first_name or 'Influencer',
                'reason': reason,
                'support_email': settings.DEFAULT_FROM_EMAIL,
            }
            
            message = f"""
Hello {context['user_name']},

Thank you for your interest in joining Collabo.

After reviewing your application, we regret to inform you that we are unable to approve your account at this time.

{f"Reason: {reason}" if reason else ""}

If you believe this is an error or would like to discuss this decision, please contact our support team at {context['support_email']}.

Best regards,
The Collabo Team
            """.strip()
            
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )
            
            logger.info(f"Rejection email sent successfully to {user.email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send rejection email to {user.email}: {str(e)}")
            return False
