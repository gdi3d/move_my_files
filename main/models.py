from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.utils.translation import ugettext as _
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.template.defaultfilters import default

from main.exceptions import *
from main.helpers import filename_pattern_transform

from threading import Thread

from tempfile import mkdtemp

import abc
import os
import fnmatch
import tempfile
import datetime
import traceback


class AbstractStorage(object):
    """ Abstract storage class """

    __metaclass__  = abc.ABCMeta
   
    @abc.abstractmethod
    def write_file(self, source_pathname, target_pathname):
        """ Write the file """

    @abc.abstractmethod
    def read_file(self, pathname):
        """ Read the file """

    @abc.abstractmethod
    def list_directory(self, pathname):
        """ Read the file """

    @abc.abstractmethod
    def file_exists(self, pathname):
        """ Check if the file exists """

    def get_files_by_wildcard(self, pathname):
        """ 
        Filter files using the * and ? wildcards 
        https://docs.python.org/2/library/fnmatch.html
        """
        base_path = os.path.dirname(pathname)
        file_pattern = os.path.basename(pathname)
        files = self.list_directory(base_path)
        
        match = list()
        for f in files:
            if fnmatch.fnmatchcase(f.lower(), file_pattern.lower()):                
                f = os.path.basename(f)
                match.append(os.path.join(base_path, f))

        return match

class Worker(Thread):

    ACTION_UPLOAD = 0
    ACTION_DOWNLOAD = 1

    ACTIONS_CHOICES = (
        (ACTION_UPLOAD, _('Upload')),
        (ACTION_DOWNLOAD, _('Download'))
    )

    def __init__(self, queue):

        super(Worker, self).__init__()
        self._queue = queue        
    
    def run(self):
        """ The code to run """
        
        while True:

            self.item = self._queue.get()            

            if self.item is None:
                break

            try:    
                if self.item.action == Worker.ACTION_DOWNLOAD:
                    transfer = self.download()
                elif self.item.action == Worker.ACTION_UPLOAD:
                    transfer = self.upload()
                else:
                    raise Exception(_('item.action is not valid. Value: %s') % str(self.item.action))
            except Exception as e:
                self.notify_task_failed(e, traceback.format_exc())
                self._queue.task_done()
            else:
                self.notify_task_finished(transfer)
                self._queue.task_done()

    def upload(self):

        from queue.models import TaskPool

        self.item.status = TaskPool.STATUS_RUNING
        self.item.save()

        task = self.item.task               
        
        # get connection type class name
        try:                 
            storage_conn = AvailableStorages.objects.get(pk = task.target_connection.storage_type.pk)
        except AvailableStorages.DoesNotExist:
            raise Exception(_("The storage id %s doesn't exists. WTF!?!") % task.target_connection.storage_type.pk)

        source_file = self.item.source_pathname
        upload_to = filename_pattern_transform(self.item.target_pathname)
        
        # set the filename for the upload file
        if '{source_filename}' in upload_to:
            upload_to_filename = os.path.basename(source_file)
            upload_to = upload_to.replace('{source_filename}', upload_to_filename)
        
        storage_conn = getattr(task.target_connection, storage_conn.class_name)

        return storage_conn.upload(source_file, upload_to)

    def download(self):

        task = self.item.task

        # get connection type class name
        try:
            storage_conn = AvailableStorages.objects.get(pk = task.source_connection.storage_type.pk)
        except AvailableStorages.DoesNotExist:
            raise Exception(_("The storage id %s doesn't exists. WTF!?!") % task.source_connection.storage_type.pk)
        
        storage_conn = getattr(task.source_connection, storage_conn.class_name)

        # get the full location of the file and replace the custom
        # date vars for the actual values
        download_from = filename_pattern_transform(self.item.source_pathname)

        # check if we need to download more than one file
        if '*' in download_from or '?' in download_from:
            download_from = storage_conn.get_files_by_wildcard(download_from)

            if not download_from:
                raise Exception(_("No files where found for the pattern: %s") % filename_pattern_transform(self.item.source_pathname))

            # add all files to the pool
            # except for the first one
            from queue.models import TaskPool
            for f in download_from[1:]:
                pool = TaskPool()
                pool.action = Worker.ACTION_DOWNLOAD
                pool.status = TaskPool.STATUS_QUEUED
                pool.task = task
                pool.source_pathname = f
                pool.target_pathname = task.target_pathname
                pool.save()

            download_from = download_from[0]

        # create a temp folder for the downloaded file
        temp_dir = mkdtemp(dir=settings.TEMP_DOWNLOAD_DIR)
                            
        # get the filename of the file we're downloading
        filename = os.path.basename(download_from)

        # create the full path to store the file on our server
        # before we upload it
        save_to = os.path.join(temp_dir, filename)
        
        return storage_conn.download(download_from, save_to)        

    def notify_task_finished(self, file_location):
        """ Actions to proccess once the task is finished """
        from queue.models import TaskPool

        if self.item.action == Worker.ACTION_DOWNLOAD:
            
            # create a new task to upload the file
            pool = TaskPool()
            pool.action = Worker.ACTION_UPLOAD
            pool.status = TaskPool.STATUS_QUEUED
            pool.task = self.item.task
            pool.source_pathname = file_location
            pool.target_pathname = self.item.task.target_pathname
            pool.save()       

        if self.item.action == Worker.ACTION_UPLOAD:            
            self.item.target_pathname = file_location

        self.item.status = TaskPool.STATUS_FINISH        
        self.item.save()       
    
    def notify_task_failed(self, error, traceback):
        
        from queue.models import TaskPool

        self.item.status = TaskPool.STATUS_FAIL
        self.item.log = str(traceback) + str(error)
        self.item.save()

        # We can't try anymore
        # send the failure mail
        if self.item.task.retry_count >= self.item.task.retries:

            if self.item.task.failure_email:

                ctx_dict = {
                    'task': self.item.task.name,
                    'date': datetime.datetime.now(),
                    'action': Worker.ACTIONS_CHOICES[self.item.action][1],
                    'error': str(error) + str(traceback)
                }

                subject = render_to_string('email/failure_email_subject.txt', ctx_dict)
                message = render_to_string('email/failure_email_message.txt', ctx_dict)
                send_to = self.item.task.failure_email_address
                
                try:
                    send_from = getattr(settings, 'NOTIFICATION_EMAIL_FROM')
                except:
                    raise Exception(_("NOTIFICATION_EMAIL_FROM is not set on settings"))
                
                if not send_to:
                    send_to = getattr(settings, 'DEFAULT_NOTIFICATION_EMAIL', None)

                if send_to is None:
                    raise Exception(_("There's no email recipient address set. Set one on the task or set DEFAULT_NOTIFICATION_EMAIL on your settings file to use it as default"))
                else:                
                    send_to = send_to.split(',')
                    send_mail(subject, message, send_from, send_to, fail_silently=True)
        else:
            # increment retry counter
            self.item.task.retry_count = self.item.task.retry_count + 1
            self.item.task.save()

            # add the task again
            pool = TaskPool()
            pool.action = self.item.action
            pool.status = TaskPool.STATUS_QUEUED
            pool.task = self.item.task
            pool.source_pathname = self.item.source_pathname
            pool.target_pathname = self.item.target_pathname
            pool.save()

class AvailableStorages(models.Model):
    name = models.CharField(max_length=255)
    class_name = models.CharField(_('Configuration Class Name'), max_length=255, help_text=_("Check the storage docs for this value"))

    def __unicode__(self):
        return u"%s" % self.name

    def save(self, *args, **kwargs):
        self.class_name = self.class_name.lower()
        super(AvailableStorages, self).save(*args, **kwargs)

class Connection(models.Model):     
    
    name = models.CharField(max_length=255) 
    notes = models.TextField(blank=True)      
    storage_type = models.ForeignKey(AvailableStorages, null=True, blank=True)

    def __unicode__(self):
        return u"%s" % self.name

    def save(self, *args, **kwargs):
        # search the type using the class name
        class_name = self.__class__.__name__
        
        try:
            storage = AvailableStorages.objects.get(class_name = class_name.lower())
        except AvailableStorages.DoesNotExist: 
            raise AvailableStorages.DoesNotExist(_("Can't find the storage %r on AvailableStorages") % class_name.lower())

        self.storage_type = storage

        super(Connection, self).save(*args, **kwargs)
    
    def connect(self):
        raise Exception(_("Method not implemented"))

    def download(self, source_pathname, target_pathname):
        try:
            self.connect()
            # check if the file exists on the remote storage
            if not self.conn.file_exists(source_pathname):
                raise FileDoesNotExists(_("The source file %r doesn't exists on remote") % source_pathname)

            # read the file and return the handler
            # to write it on local disk
            download = self.conn.read_file(source_pathname)

            from local_storage.models import LocalStorage

            local = LocalStorage()
            local.write_file(download, target_pathname)
        except:
            raise
        else:
            return target_pathname

    def upload(self, source_pathname, target_pathname):
        try:
            from local_storage.models import LocalStorage

            local = LocalStorage()
            # check if file exists on local disk
            if not local.file_exists(source_pathname):                
                raise FileDoesNotExists(_("The source file %r doesn't exists on local") % source_pathname)            
            
            self.connect()
            # check if file exists on remote            
            if self.conn.file_exists(target_pathname):
                raise FileExists(_("The target file %r already exists on remote") % target_pathname)     
            
            self.conn.write_file(source_pathname, target_pathname)
        except:
            raise
        else:
            return target_pathname

    def get_files_by_wildcard(self, pathname):
        self.connect()
        return self.conn.get_files_by_wildcard(pathname)        

class Task(models.Model):

    source_connection = models.ForeignKey('Connection', related_name="id_source_connection", help_text=_("Source connection"))
    target_connection = models.ForeignKey('Connection', related_name="id_destination_connection", help_text=_("Destination connection"))
    name        = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    source_pathname = models.CharField(max_length=255, help_text=_("You can also use python date formats: %D, %m, etc"))
    target_pathname = models.CharField(max_length=255, help_text=_('Use {source_filename} if you want to use the same filename. You can also use python date formats: %D, %m, etc'), default='{source_filename}')      
    failure_email   = models.BooleanField(_("Send email on Failure"), default=True)
    failure_email_address = models.EmailField(_("Email Address"), blank=True, help_text=_('If empty will use DEFAULT_NOTIFICATION_EMAIL from settings'))
    retries     = models.SmallIntegerField(_('Max. Retries'), default=3)
    retry_count = models.SmallIntegerField(default=0, help_text=_("Internal use, don't change it"))
    
    def __unicode__(self):
        return self.name

    def add_to_pool(self):
        """ Split the task into two pieces """

        from queue.models import TaskPool        
        # download task
        pool = TaskPool()
        pool.task = self
        pool.action = Worker.ACTION_DOWNLOAD
        pool.status = TaskPool.STATUS_QUEUED
        pool.source_pathname = self.source_pathname
        pool.target_pathname = self.target_pathname
        pool.save()

class SchedulerManager(models.Manager):
    
    def task_availabes(self):
        now = datetime.datetime.now()
        return self.filter(start_date__lte = now, end_date__gte = now, enabled = True)
        
class Scheduler(models.Model):
    
    INTERVAL_TYPE_MINUTES = 0
    INTERVAL_TYPE_HOURS = 1
    INTERVAL_TYPE_DAYS = 2

    INTERVAL_TYPES_CHOICES = (
        (INTERVAL_TYPE_MINUTES, _('Minutes')),
        (INTERVAL_TYPE_HOURS, _('Hours')),
        (INTERVAL_TYPE_DAYS, _('Days'))
    )
    
    task        = models.ForeignKey('Task')
    start_date  = models.DateTimeField()
    end_date    = models.DateTimeField()
    recurrent   = models.BooleanField(default=False)
    repeat_interval_type = models.SmallIntegerField(choices=INTERVAL_TYPES_CHOICES, blank=True)
    repeat_interval = models.IntegerField(blank=True)
    enabled      = models.BooleanField(default=True)    
    
    objects = SchedulerManager()

    def __unicode__(self):
        return unicode(self.task)