from django.db import models
from django.utils.translation import ugettext as _

from main.models import AbstractStorage, Connection, AvailableStorages
from main.exceptions import *

import os

class LocalStorage(AbstractStorage):
    """ Filesystem API Storage. """

    def _connect(self):
        pass

    def list_directory(self, path):
        """ List all files inside a directory. """
        files = [ f for f in os.listdir(path) if os.path.isfile(os.path.join(path,f)) ]
        return files

    def write_file(self, source_pathname, target_filename):
        """ 
        Write the specified file. 
        :param source_pathname: The source_pathname file
        :type source_pathname: File Object or String
        """        
        # check if it's a file-like or string
        # because most of the time we will
        # use this method to write to disk
        # file handlers returned from the read_file
        # methods of remote storages.
        # Ex: S3Storage.read_file(...)
        # will return SpooledTemporaryFile handle
        # and we will pass that to this method
        # to store the downloaded file on disk
        try:
            source_pathname.seek(0)
        except AttributeError:
            source_pathname = open(source_pathname, 'rb')
        except:
            raise
        
        target_file = open(target_filename, 'wb')
        
        data = source_pathname.read(1024)
        while data:
            try:
                target_file.write(data)
            except IOError:
                raise StorageError(_("Coudn't write the file: %r") % target_file)
            else:   
                data = source_pathname.read(1024)

        target_file.close()
        return target_file

    def read_file(self, filepath):
        """ Read the specified file and return it's handle. """
        return open(filepath, 'rb')   
    
    def file_exists(self, pathname):
        return os.path.isfile(pathname)

class LocalStorageConnectionSettings(Connection):
    """ Local Storage Settings model """

    def __unicode__(self):
        return "Local Storage: %s" % self.name

    def connect(self):
        """ Create an connection instance if doens't exists """
        if not hasattr(self, 'conn'):
            self.conn = LocalStorage()