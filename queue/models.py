from django.db import models
from django.utils.translation import ugettext as _

from main.models import Task, Worker

# Create your models here.
class TaskPool(models.Model):

	STATUS_QUEUED = 0
	STATUS_RUNING = 1
	STATUS_FINISH = 2
	STATUS_FAIL = 3

	STATUS_CHOICES = (
		(STATUS_QUEUED, _('On queue')),
		(STATUS_RUNING, _('Runing')),
		(STATUS_FINISH, _('Finish :)')),
		(STATUS_FAIL, _('Fail :('))
	)

	task = models.ForeignKey(Task)
	status = models.SmallIntegerField(choices=STATUS_CHOICES)
	action = models.SmallIntegerField(choices=Worker.ACTIONS_CHOICES)
	source_pathname = models.CharField(_("Source Location"), max_length=255, blank=True, help_text=_("Once downloaded this will be the pathname on local disk"))
	target_pathname = models.CharField(max_length=255, blank=True)
	created = models.DateTimeField(auto_now_add=True)
	modified = models.DateTimeField(auto_now=True)
	log = models.TextField(blank=True, null=True)

	def __unicode__(self):
		return u"%s (%s)" % (self.task.name, Worker.ACTIONS_CHOICES[self.action][1])