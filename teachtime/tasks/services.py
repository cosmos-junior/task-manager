import urllib.request
import urllib.parse
import json
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
import logging

logger = logging.getLogger(__name__)

class NotificationService:
    
    @staticmethod
    def send_email_reminder(user, tasks):
        """Send email reminder with daily tasks"""
        try:
            subject = f"Daily Task Reminder - {user.first_name or user.username}"
            
            # Create email content
            context = {
                'user': user,
                'tasks': tasks,
                'incomplete_tasks': [t for t in tasks if not t.completed],
                'completed_tasks': [t for t in tasks if t.completed],
                'site_url': settings.SITE_URL
            }
            
            message = render_to_string('tasks/email_reminder.html', context)
            plain_message = render_to_string('tasks/email_reminder.txt', context)
            
            send_mail(
                subject=subject,
                message=plain_message,
                html_message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )
            
            logger.info(f"Email reminder sent to {user.email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {user.email}: {str(e)}")
            return False
    
    @staticmethod
    def send_sms_reminder(user, tasks):
        """Send SMS reminder using Twilio API"""
        try:
            if not hasattr(user, 'profile') or not user.profile.phone_number:
                logger.warning(f"No phone number for user {user.username}")
                return False
            
            # Count incomplete tasks
            incomplete_count = len([t for t in tasks if not t.completed])
            
            if incomplete_count == 0:
                message = f"Hi {user.first_name or user.username}! 🎉 All your tasks are complete for today!"
            else:
                message = f"Hi {user.first_name or user.username}! You have {incomplete_count} pending task{'s' if incomplete_count > 1 else ''} today. Check your dashboard: {settings.SITE_URL}"
            
            # Twilio API call using urllib
            import base64
            
            data = urllib.parse.urlencode({
                'From': settings.TWILIO_PHONE_NUMBER,
                'To': user.profile.phone_number,
                'Body': message
            }).encode('utf-8')
            
            credentials = f"{settings.TWILIO_ACCOUNT_SID}:{settings.TWILIO_AUTH_TOKEN}"
            encoded_credentials = base64.b64encode(credentials.encode()).decode()
            
            req = urllib.request.Request(
                f"https://api.twilio.com/2010-04-01/Accounts/{settings.TWILIO_ACCOUNT_SID}/Messages.json",
                data=data,
                headers={
                    'Authorization': f'Basic {encoded_credentials}',
                    'Content-Type': 'application/x-www-form-urlencoded'
                }
            )
            
            try:
                response = urllib.request.urlopen(req)
                if response.status == 201:
                    logger.info(f"SMS sent to {user.profile.phone_number}")
                    return True
                else:
                    logger.error(f"Twilio API error: {response.status}")
                    return False
            except urllib.error.HTTPError as e:
                logger.error(f"Twilio API error: {e.read().decode()}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to send SMS to {user.username}: {str(e)}")
            return False
    
    @staticmethod
    def send_push_notification(user, tasks):
        """Send push notification using Firebase or similar service"""
        try:
            incomplete_count = len([t for t in tasks if not t.completed])
            
            if incomplete_count == 0:
                title = "All Done! 🎉"
                body = "You've completed all your tasks for today!"
            else:
                title = f"Task Reminder ({incomplete_count} pending)"
                body = f"You have {incomplete_count} task{'s' if incomplete_count > 1 else ''} waiting for you."
            
            # Firebase Cloud Messaging API call
            headers = {
                'Authorization': f'key={settings.FCM_SERVER_KEY}',
                'Content-Type': 'application/json',
            }
            
            payload = {
                'to': user.profile.fcm_token if hasattr(user, 'profile') and user.profile.fcm_token else None,
                'notification': {
                    'title': title,
                    'body': body,
                    'icon': '/static/icon-192x192.png',
                    'click_action': settings.SITE_URL
                },
                'data': {
                    'url': settings.SITE_URL,
                    'task_count': str(incomplete_count)
                }
            }
            
            if not payload['to']:
                logger.warning(f"No FCM token for user {user.username}")
                return False
            
            req = urllib.request.Request(
                'https://fcm.googleapis.com/fcm/send',
                data=json.dumps(payload).encode('utf-8'),
                headers=headers
            )
            
            try:
                response = urllib.request.urlopen(req)
                if response.status == 200:
                    logger.info(f"Push notification sent to {user.username}")
                    return True
                else:
                    logger.error(f"FCM API error: {response.status}")
                    return False
            except urllib.error.HTTPError as e:
                logger.error(f"FCM API error: {e.read().decode()}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to send push notification to {user.username}: {str(e)}")
            return False