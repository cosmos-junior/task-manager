from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    fcm_token = models.TextField(blank=True, null=True)  # For push notifications
    email_reminders = models.BooleanField(default=True)
    sms_reminders = models.BooleanField(default=False)
    push_reminders = models.BooleanField(default=True)
    reminder_time = models.TimeField(default='08:00')  # Daily reminder time
    buffer_time = models.FloatField(default=2.0)
    
    def __str__(self):
        return f"{self.user.username}'s Profile"

class Task(models.Model):
    PRIORITY_CHOICES = [
        ('high', 'High Priority'),
        ('medium', 'Medium Priority'),
        ('low', 'Low Priority'),
        ('flexible', 'Flexible (Can Shift)'),
    ]
    
    CATEGORY_CHOICES = [
        ('church', 'Church Leadership'),
        ('weekend', 'Weekend Commitments'),
        ('personal', 'Personal'),
        ('work', 'Work'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks')
    text = models.CharField(max_length=255)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    category = models.CharField(max_length=10, choices=CATEGORY_CHOICES, default='personal')
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    due_date = models.DateField(default=timezone.now)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.text} ({self.get_priority_display()})"

class ReminderLog(models.Model):
    REMINDER_TYPES = [
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('push', 'Push Notification'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reminder_type = models.CharField(max_length=10, choices=REMINDER_TYPES)
    sent_at = models.DateTimeField(auto_now_add=True)
    success = models.BooleanField(default=False)
    error_message = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-sent_at']
    
    def __str__(self):
        status = "✓" if self.success else "✗"
        return f"{status} {self.get_reminder_type_display()} to {self.user.username}"