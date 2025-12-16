from django.db import models
from django.contrib.auth.models import User
# Create your models here.
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
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.CharField(max_length=500)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    category = models.CharField(max_length=10, choices=CATEGORY_CHOICES, default='personal')
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.text


class UserSettings(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    buffer_time = models.FloatField(default=2.0)
    
    def __str__(self):
        return f"{self.user.username}'s settings"
