from django.db import models
from django.conf import settings
from django.utils.translation import ugettext as _

from main.models import AbstractStorage, Connection, AvailableStorages
from main.exceptions import *

from local_storage.models import LocalStorage

from tempfile import SpooledTemporaryFile
from ftplib import FTP, error_perm

import os

class FtpStorage(AbstractStorage):
    """ FTP API Storage """
    
    def __init__(self, host, user, password, port):        
        
        self.host = host + ':' + str(port)
        self.user = user
        self.password = password
        self.passive_mode = passive_mode

        self.conn = FTP(self.host, self.user, self.password, timeout=60)        
        self.conn.set_pasv(True)

        # enable this when you're debugging
        #self.conn.set_debuglevel(3)
    
    def delete_file(self, filepath):
        """ Delete the specified filepath. """
        self.conn.delete(filepath)

    def list_directory(self, path):
        """ List all files on the specified directory. """             
        return sorted(self.conn.nlst(path))

    def write_file(self, source_pathname, target_pathname):
        """ Write the specified file. """        
        
        source_pathname = open(source_pathname, 'rb')
        source_pathname.seek(0)
        
        path = os.path.dirname(target_pathname)       
        
        try:
            open_dir = self.open_dir(path)
        except:
            raise                
        
        path = os.path.join(path, target_pathname)
        
        try:             
            self.conn.storbinary('STOR ' + path, source_pathname)
        except:
            raise
        
        return target_pathname

    def open_dir(self, path, create=True):
        try:
            self.conn.cwd(path)
        except Exception:
            if(create):
                try:              
                    self.conn.mkd(path)
                    self.open_dir(path, False)
                except Exception:
                    raise StorageError(_("The path couldn't be created: %s") % path)
            else:
                raise StorageError(_("The path %r doens't exists") % path)
            
    def read_file(self, pathname):
        """ Read the specified file and return it's handle. """        
        try:            
            handle = SpooledTemporaryFile(max_size=10 * 1024 * 1024)
        except:
            raise
        
        try:        
            self.conn.retrbinary('RETR ' + pathname, handle.write)
        except:
            raise
        
        return handle
    
    def file_exists(self, pathname):
        f = self.list_directory(pathname)
        return not not f
            
    def close(self):
        self.conn.close()

class FtpConnectionSettings(Connection):
    """ Ftp model """
    host = models.CharField(max_length=250)
    port = models.IntegerField()
    username = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    
    def __unicode__(self):
        return "Ftp: %s - Url: %s" % (self.name, self.host)
    
    def connect(self):
        if not hasattr(self, 'conn'):
            try:                
                self.conn = FtpStorage(self.host, self.username, self.password, self.port, self.passive)
            except:
                raise ConnectionFailed(_("Coundn't connect to FTP: %s") % self.host)