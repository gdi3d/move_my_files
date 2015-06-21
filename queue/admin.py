from django.contrib import admin
from queue.models import TaskPool

# Register your models here.
class TaskPoolAdmin(admin.ModelAdmin):
	list_display = ('task', 'action', 'status', 'created', 'modified')
	list_filter = ('action', 'status', 'modified', 'created', 'task__name')

admin.site.register(TaskPool, TaskPoolAdmin)