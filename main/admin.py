from django.contrib import admin
from main.models import Task, AvailableStorages, Scheduler
from django import forms

admin.site.register(Task)
admin.site.register(AvailableStorages)
admin.site.register(Scheduler)