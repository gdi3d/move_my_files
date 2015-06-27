from django.test import TestCase
from s3_storage.models import S3Storage

from time import sleep

import boto
import tempfile
import os

# Create your tests here.
class S3StorageFunctionalTest(TestCase):

	def setUp(self):
		""" 
		IMPORTANT
		All files created on S3 for this test ARE NOT DELETED
		ON tearDown for security reasons.
		
		Also notice that all test are named test_NUMBER_...
		that's just an ugly hack to force order
		"""
		self._temp_files = list()
		
		# set your keys and bucket name to run this test
		self.access_key = ''
		self.secret_key = ''
		self.is_secure = True
		self.bucket = ''

		# Config for test_write_file_success method		
		self.temp_file_content = "Hello, can you see me?"
		self.temp_file_key_on_s3 = 'test-you-can-delete-me.txt'
		
		# write  a temp file to upload
		self.temp_file = tempfile.NamedTemporaryFile(delete = False)
		self.temp_file.write(self.temp_file_content)
		self.temp_file.close()		
		
		self._temp_files.append(self.temp_file.name)

		# config for test_list_directory method		
		self.directory_list = 'test-delete-me'
		self.directory_list_return_results = [
			u'test-delete-me/foo.bar',
			u'test-delete-me/bar.foo',
			u'test-delete-me/farboo'
		]

		# connect to S3
		self.s3 = S3Storage(self.access_key, self.secret_key, self.bucket, self.is_secure)

	def test_1_write_file_success(self):

		write = self.s3.write_file(self.temp_file.name, self.temp_file_key_on_s3)
		self.assertTrue(type(write) is boto.s3.multipart.CompleteMultiPartUpload)

	def test_2_read_file_success(self):

		read = self.s3.read_file(self.temp_file_key_on_s3)
		read.seek(0)
		self.assertEqual(read.read(len(self.temp_file_content)), self.temp_file_content)

	def test_3_file_exists_success(self):

		exists = self.s3.file_exists(self.temp_file_key_on_s3)
		self.assertTrue(exists)

	def test_4_list_directory(self):

		# create files on S3
		for f in self.directory_list_return_results:
			
			temp = tempfile.NamedTemporaryFile(delete = False)
			temp.write(f)
			temp.close()
			self._temp_files.append(temp.name)
			self.s3.write_file(temp.name, f)

		files = self.s3.list_directory(self.directory_list)
		self.assertItemsEqual(files, self.directory_list_return_results)

	def tearDown(self):

		# delete temp files from disk
		for f in self._temp_files:
			os.unlink(f)



