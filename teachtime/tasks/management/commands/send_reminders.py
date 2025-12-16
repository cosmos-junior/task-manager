from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from tasks.models import Task, ReminderLog
from tasks.services import NotificationService
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Send daily task reminders to users'

    def add_arguments(self, parser):
        parser.add_argument(
            '--user',
            type=str,
            help='Send reminder to specific user (username)',
        )
        parser.add_argument(
            '--type',
            type=str,
            choices=['email', 'sms', 'push', 'all'],
            default='all',
            help='Type of reminder to send',
        )

    def handle(self, *args, **options):
        users = User.objects.all()
        
        if options['user']:
            users = users.filter(username=options['user'])
        
        # Filter users who should receive reminders at this time
        current_time = timezone.now().time()
        users = users.filter(
            profile__reminder_time__hour=current_time.hour,
            profile__reminder_time__minute__lte=current_time.minute + 5,
            profile__reminder_time__minute__gte=current_time.minute - 5
        )
        
        reminder_type = options['type']
        total_sent = 0
        
        for user in users:
            try:
                # Get today's tasks
                today = timezone.now().date()
                tasks = Task.objects.filter(user=user, due_date=today)
                
                if not tasks.exists():
                    continue
                
                # Send reminders based on user preferences
                if reminder_type in ['email', 'all'] and user.profile.email_reminders:
                    success = NotificationService.send_email_reminder(user, tasks)
                    self.log_reminder(user, 'email', success)
                    if success:
                        total_sent += 1
                
                if reminder_type in ['sms', 'all'] and user.profile.sms_reminders:
                    success = NotificationService.send_sms_reminder(user, tasks)
                    self.log_reminder(user, 'sms', success)
                    if success:
                        total_sent += 1
                
                if reminder_type in ['push', 'all'] and user.profile.push_reminders:
                    success = NotificationService.send_push_notification(user, tasks)
                    self.log_reminder(user, 'push', success)
                    if success:
                        total_sent += 1
                        
            except Exception as e:
                logger.error(f"Error sending reminder to {user.username}: {str(e)}")
                self.log_reminder(user, reminder_type, False, str(e))
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully sent {total_sent} reminders')
        )
    
    def log_reminder(self, user, reminder_type, success, error_message=None):
        """Log reminder attempt"""
        ReminderLog.objects.create(
            user=user,
            reminder_type=reminder_type,
            success=success,
            error_message=error_message
        )