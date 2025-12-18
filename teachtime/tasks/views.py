from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from .models import Task, UserProfile, ReminderLog
from .services import NotificationService
import json

# Create your views here.

@login_required
def dashboard(request):
    tasks = Task.objects.filter(user=request.user)
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    context = {
        'tasks': tasks,
        'buffer_time': profile.buffer_time,
    }
    return render(request, 'tasks/dashboard.html', context)

@login_required
@require_POST
def add_task(request):
    data = json.loads(request.body)
    task = Task.objects.create(
        user=request.user,
        text=data.get('text'),
        priority=data.get('priority', 'medium'),
        category=data.get('category', 'personal')
    )
    return JsonResponse({
        'id': task.id,
        'text': task.text,
        'priority': task.priority,
        'category': task.category,
        'completed': task.completed
    })

@login_required
@require_POST
def toggle_task(request, task_id):
    task = get_object_or_404(Task, id=task_id, user=request.user)
    task.completed = not task.completed
    task.save()
    return JsonResponse({'completed': task.completed})

@login_required
@require_POST
def delete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id, user=request.user)
    task.delete()
    return JsonResponse({'success': True})

@login_required
@require_POST
def update_buffer(request):
    data = json.loads(request.body)
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    profile.buffer_time = float(data.get('buffer_time', 2.0))
    profile.save()
    return JsonResponse({'buffer_time': profile.buffer_time})

@login_required
@require_POST
def send_reminder_now(request):
    """REST API endpoint to send immediate reminder"""
    data = json.loads(request.body)
    reminder_type = data.get('type', 'email')
    
    # Get today's tasks
    today = timezone.now().date()
    tasks = Task.objects.filter(user=request.user, due_date=today)
    
    success = False
    message = ""
    
    try:
        if reminder_type == 'email':
            success = NotificationService.send_email_reminder(request.user, tasks)
            message = "Email reminder sent successfully" if success else "Failed to send email"
        elif reminder_type == 'sms':
            success = NotificationService.send_sms_reminder(request.user, tasks)
            message = "SMS reminder sent successfully" if success else "Failed to send SMS"
        elif reminder_type == 'push':
            success = NotificationService.send_push_notification(request.user, tasks)
            message = "Push notification sent successfully" if success else "Failed to send push notification"
        else:
            return JsonResponse({'error': 'Invalid reminder type'}, status=400)
        
        # Log the reminder
        ReminderLog.objects.create(
            user=request.user,
            reminder_type=reminder_type,
            success=success
        )
        
        return JsonResponse({
            'success': success,
            'message': message,
            'task_count': tasks.count()
        })
        
    except Exception as e:
        ReminderLog.objects.create(
            user=request.user,
            reminder_type=reminder_type,
            success=False,
            error_message=str(e)
        )
        return JsonResponse({'error': str(e)}, status=500)

@login_required
@require_http_methods(["GET", "POST"])
def notification_settings(request):
    """REST API endpoint to get/update notification settings"""
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'GET':
        return JsonResponse({
            'email_reminders': profile.email_reminders,
            'sms_reminders': profile.sms_reminders,
            'push_reminders': profile.push_reminders,
            'reminder_time': profile.reminder_time.strftime('%H:%M'),
            'phone_number': profile.phone_number or '',
        })
    
    elif request.method == 'POST':
        data = json.loads(request.body)
        
        profile.email_reminders = data.get('email_reminders', profile.email_reminders)
        profile.sms_reminders = data.get('sms_reminders', profile.sms_reminders)
        profile.push_reminders = data.get('push_reminders', profile.push_reminders)
        
        if 'reminder_time' in data:
            from datetime import datetime
            profile.reminder_time = datetime.strptime(data['reminder_time'], '%H:%M').time()
        
        if 'phone_number' in data:
            profile.phone_number = data['phone_number']
        
        if 'fcm_token' in data:
            profile.fcm_token = data['fcm_token']
        
        profile.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Settings updated successfully'
        })

@login_required
def reminder_history(request):
    """REST API endpoint to get reminder history"""
    logs = ReminderLog.objects.filter(user=request.user)[:20]
    
    history = []
    for log in logs:
        history.append({
            'type': log.get_reminder_type_display(),
            'sent_at': log.sent_at.isoformat(),
            'success': log.success,
            'error_message': log.error_message
        })
    
    return JsonResponse({'history': history})

@login_required
def settings_page(request):
    """Settings page for notification preferences"""
    return render(request, 'tasks/settings.html')


# ============= tasks/urls.py =============
from django.urls import path
from . import views

app_name = 'tasks'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('add/', views.add_task, name='add_task'),
    path('toggle/<int:task_id>/', views.toggle_task, name='toggle_task'),
    path('delete/<int:task_id>/', views.delete_task, name='delete_task'),
    path('update-buffer/', views.update_buffer, name='update_buffer'),
    # Settings page
    path('settings/', views.settings_page, name='settings'),
    # Notification API endpoints
    path('api/send-reminder/', views.send_reminder_now, name='send_reminder'),
    path('api/notification-settings/', views.notification_settings, name='notification_settings'),
    path('api/reminder-history/', views.reminder_history, name='reminder_history'),
]
