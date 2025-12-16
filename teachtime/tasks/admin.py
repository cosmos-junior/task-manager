from django.contrib import admin
from .models import Task, UserProfile, ReminderLog

# Register your models here.

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['text', 'user', 'priority', 'category', 'completed', 'created_at']
    list_filter = ['priority', 'category', 'completed', 'created_at']
    search_fields = ['text', 'user__username']

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone_number', 'email_reminders', 'sms_reminders', 'reminder_time', 'buffer_time']
    list_filter = ['email_reminders', 'sms_reminders', 'push_reminders']

@admin.register(ReminderLog)
class ReminderLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'reminder_type', 'success', 'sent_at']
    list_filter = ['reminder_type', 'success', 'sent_at']
    readonly_fields = ['sent_at']
