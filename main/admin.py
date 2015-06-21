from django.contrib import admin
from main.models import Task, AvailableStorages, Scheduler
from django import forms

class TaskForm(forms.ModelForm):

    class Meta:
        model = Task
        exclude = ['retry_count']

class AdminTaskForm(admin.ModelAdmin):
	form = TaskForm

admin.site.register(Task, AdminTaskForm)
admin.site.register(AvailableStorages)
admin.site.register(Scheduler)