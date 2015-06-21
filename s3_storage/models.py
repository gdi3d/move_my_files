from django.db import models
from django.conf import settings
from django.utils.translation import ugettext as _

from boto.s3.key import Key
from boto.s3.connection import S3Connection

from tempfile import SpooledTemporaryFile

from main.models import AbstractStorage, AvailableStorages, Connection
from main.exceptions import *

from local_storage.models import LocalStorage

from filechunkio import FileChunkIO

import math
import os

class S3Storage(AbstractStorage):
    """ S3 API Storage. """

    def __init__(self, access_key, secret_key, bucket, secure):
        
        self.conn = S3Connection(aws_access_key_id=access_key, aws_secret_access_key=secret_key, is_secure=secure)
        self.bucket = self.conn.get_bucket(self.bucket)    

    def delete_file(self, filepath):
        self.bucket.delete_key(filepath)

    def list_directory(self, path):
        return [k.name for k in self.bucket.list(prefix=path)]

    def write_file(self, source_pathname, target_pathname = None):
        # Use multipart upload because normal upload maximum is 5 GB.       

        source_path = source_pathname
        source_size = os.stat(source_path).st_size

        if not target_pathname:
            target_pathname = os.path.basename(source_path)

        # Create a multipart upload request
        mp = self.bucket.initiate_multipart_upload(target_pathname)

        # Use a chunk size of 50 MiB (feel free to change this)
        chunk_size = 5242880
        chunk_count = int(math.ceil(source_size / float(chunk_size)))

        # Send the file parts, using FileChunkIO to create a file-like object
        # that points to a certain byte range within the original file. We
        # set bytes to never exceed the original file size.
        try:
            for i in range(chunk_count):
                offset = chunk_size * i                
                bytes = min(chunk_size, source_size - offset)
                with FileChunkIO(source_path, 'r', offset=offset,
                                     bytes=bytes) as fp:
                    mp.upload_part_from_file(fp, part_num=i + 1)
            
            # Finish the upload
            uploaded_file = mp.complete_upload()
        except:
            mp.cancel_upload()
            raise
        else:
            return uploaded_file

    def read_file(self, pathname):
        """ Read the specified file and return it's handle. """
        key = Key(self.bucket)
        key.key = pathname
        filehandle = SpooledTemporaryFile(max_size=10 * 1024 * 1024)
        key.get_contents_to_file(filehandle)
        return filehandle

    def file_exists(self, pathname):
        key = Key(self.bucket)
        key.key = pathname

        return key.exists()

class S3ConnectionSettings(Connection):
    """ Configuration model """
    bucket = models.CharField(max_length=255)
    access_key = models.CharField(max_length=255)
    secret_key = models.CharField(max_length=255)
    secure = models.BooleanField()
    
    def __unicode__(self):
        return "S3 Configuration: %s - Bucket: %s" % (self.name, self.bucket)

    def connect(self):
        if not hasattr(self, 'conn'):
            try:
                self.conn = S3Storage(self.access_key, self.secret_key, self.bucket, self.secure)
            except:
                raise ConnectionFailed(_("Couldn't connect to S3 %s") % self.bucket)