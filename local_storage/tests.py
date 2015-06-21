from django.test import TestCase
from local_storage.models import LocalStorage, LocalStorageConnectionSettings
from main.exceptions import *
import mock

# Create your tests here.
class LocalStorageConnectionSettingsTestCase(TestCase):

	def test_connect(self):
		local = LocalStorageConnectionSettings()		
		local.connect()

		self.assertEqual(type(local.conn), type(LocalStorage()))

	def test_download_raise_source_file_dont_exists(self):
		
		mock_storage = mock.create_autospec(LocalStorage)
		mock_storage.file_exists = mock.Mock(return_value=False)

		local = LocalStorageConnectionSettings()
		local.conn = mock_storage
		
		file_dont_exists = False
		try:
			local.download('foo.bar', 'bar.foo')
		except FileDoesNotExists:
			file_dont_exists = True

		self.assertTrue(file_dont_exists)

	def test_download_raise_remote_file_dont_exists(self):

		mock_storage = mock.create_autospec(LocalStorage)
		mock_storage.file_exists = mock.Mock(return_value=True)
		mock_storage.write_file = mock.Mock(side_effect=Exception())

		local = LocalStorageConnectionSettings()
		local.conn = mock_storage

		download_fail = False
		try:
			local.download('foo.bar', 'bar.foo')
		except Exception:
			download_fail = True

		self.assertTrue(download_fail)

	@mock.patch.object(LocalStorage, 'write_file')
	def test_download_success(self, mock_localstorage_write):

		local = LocalStorageConnectionSettings()

		mock_storage = mock.create_autospec(LocalStorage)
		mock_storage.file_exists = mock.Mock(return_value=True)	
		mock_storage.write_file = mock.Mock(return_value=True)	

		local.conn = mock_storage

		mock_localstorage_write.return_value = 'target_pathname'		

		value = local.download('sourch_pathname.txt', 'target_pathname.txt')

		self.assertEqual(value, 'target_pathname.txt')

	def test_upload_raise_source_file_on_local_dont_exists(self):
		
		mock_storage = mock.create_autospec(LocalStorage)
		mock_storage.file_exists = mock.Mock(return_value=False)

		local = LocalStorageConnectionSettings()
		local.conn = mock_storage
		
		file_dont_exists = False
		try:
			local.upload('foo.bar', 'bar.foo')
		except FileDoesNotExists:
			file_dont_exists = True

		self.assertTrue(file_dont_exists)

	@mock.patch.object(LocalStorage, 'file_exists')
	def test_upload_raise_file_exists_on_remote(self, mock_local_storage_file_exists):

		mock_storage = mock.create_autospec(LocalStorage)
		mock_storage.file_exists = mock.Mock(return_value=True)

		local = LocalStorageConnectionSettings()
		local.conn = mock_storage

		mock_local_storage_file_exists.return_value = True

		file_exists = False
		try:
			local.upload('foo.bar', 'bar.foo')
		except FileExists:
			file_exists = True

		self.assertTrue(file_exists)

	@mock.patch.object(LocalStorage, 'file_exists')
	def test_upload_success(self, mock_local_storage_file_exists):

		local = LocalStorageConnectionSettings()

		mock_storage = mock.create_autospec(LocalStorage)
		mock_storage.file_exists = mock.Mock(return_value=False)
		mock_storage.write_file = mock.Mock(return_value='target_pathname.txt')

		local.conn = mock_storage

		value = local.upload('sourch_pathname.txt', 'target_pathname.txt')

		self.assertEqual(value, 'target_pathname.txt')

	@mock.patch.object(LocalStorage, 'file_exists')
	def test_upload_raise_remote_file_exists(self, mock_local_storage_file_exists):
		
		mock_storage = mock.create_autospec(LocalStorage)
		mock_storage.file_exists = mock.Mock(return_value=True)

		local = LocalStorageConnectionSettings()
		local.conn = mock_storage
		
		file_exists = False
		try:
			local.upload('foo.bar', 'bar.foo')
		except FileExists:
			file_exists = True

		self.assertTrue(file_exists)