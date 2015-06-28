from django.test import TestCase
from ftp_storage.models import FtpStorage

from time import sleep

import boto
import tempfile
import os

# Create your tests here.
class FTPStorageFunctionalTest(TestCase):

	def setUp(self):
		""" 
		IMPORTANT
		All files created on FTP for this test ARE NOT DELETED
		ON tearDown for security reasons.
		
		Also notice that all test are named test_NUMBER_...
		that's just an ugly hack to force order
		"""
		self._temp_files = list()
		
		# set your credentials
		self.host = ''
		self.port = 21
		self.user = ''
		self.password = ''

		# Config for test_write_file_success method		
		self.temp_file_content = "Hello, can you see me?"
		self.temp_file_on_ftp = 'test-you-can-delete-me.txt'
		
		# write  a temp file to upload
		self.temp_file = tempfile.NamedTemporaryFile(delete = False)
		self.temp_file.write(self.temp_file_content)
		self.temp_file.close()		
		
		self._temp_files.append(self.temp_file.name)

		# config for test_list_directory method		
		self.directory_list = '/test-delete-me'
		self.directory_list_return_results = [
			'.',
			'..',
			'/test-delete-me/foo.bar',
			'/test-delete-me/bar.foo',
			'/test-delete-me/farboo'
		]

		# connect to FTP
		self.ftp = FtpStorage(self.host, self.user, self.password, self.port)

	def test_1_write_file_success(self):

		write = self.ftp.write_file(self.temp_file.name, self.temp_file_on_ftp)
		self.assertEqual(write, self.temp_file_on_ftp)

	def test_2_read_file_success(self):

		read = self.ftp.read_file(self.temp_file_on_ftp)
		read.seek(0)
		self.assertEqual(read.read(len(self.temp_file_content)), self.temp_file_content)

	def test_3_file_exists_success(self):

		exists = self.ftp.file_exists(self.temp_file_on_ftp)
		self.assertTrue(exists)

	def test_4_list_directory(self):

		# create files on FTP
		for f in self.directory_list_return_results[2:]:
			
			temp = tempfile.NamedTemporaryFile(delete = False)
			temp.write(f)
			temp.close()
			self._temp_files.append(temp.name)
			self.ftp.write_file(temp.name, f)

		files = self.ftp.list_directory(self.directory_list)
		
		# remove the path from the list
		compare = []
		for f in self.directory_list_return_results:
			compare.append(os.path.basename(f))

		self.assertItemsEqual(files, compare)

	def tearDown(self):

		self.ftp.close()

		# delete temp files from disk
		for f in self._temp_files:
			os.unlink(f)



