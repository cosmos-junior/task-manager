from django.urls import path
from . import views

app_name = 'tasks'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('add/', views.add_task, name='add_task'),
    path('toggle/<int:task_id>/', views.toggle_task, name='toggle_task'),
    path('delete/<int:task_id>/', views.delete_task, name='delete_task'),
    path('update-buffer/', views.update_buffer, name='update_buffer'),
    path('settings/', views.settings_page, name='settings'),
    path('api/send-reminder/', views.send_reminder_now, name='send_reminder'),
    path('api/notification-settings/', views.notification_settings, name='notification_settings'),
    path('api/reminder-history/', views.reminder_history, name='reminder_history'),
]
