from django.shortcuts import render
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Task, UserSettings
import json

# Create your views here.

@login_required
def dashboard(request):
    tasks = Task.objects.filter(user=request.user)
    settings, created = UserSettings.objects.get_or_create(user=request.user)
    
    context = {
        'tasks': tasks,
        'buffer_time': settings.buffer_time,
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
    settings, created = UserSettings.objects.get_or_create(user=request.user)
    settings.buffer_time = float(data.get('buffer_time', 2.0))
    settings.save()
    return JsonResponse({'buffer_time': settings.buffer_time})


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
]
