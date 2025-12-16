from django.contrib import admin
from .models import Task, UserSettings

# Register your models here.

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['text', 'user', 'priority', 'category', 'completed', 'created_at']
    list_filter = ['priority', 'category', 'completed', 'created_at']
    search_fields = ['text', 'user__username']

@admin.register(UserSettings)
class UserSettingsAdmin(admin.ModelAdmin):
    list_display = ['user', 'buffer_time']
