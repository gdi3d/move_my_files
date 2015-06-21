from django.test import TestCase
from main.models import Worker, Task, Connection
from main.exceptions import *
from queue.models import TaskPool
from Queue import Queue
import mock
# Create your tests here.
class WorkerTestCase(TestCase):

    def test_worker_upload_raise_available_storage_dont_exists(self):
        """ """
        task_pool = Queue(maxsize=0)

        # mocks
        mock_task = mock.create_autospec(Task)
        mock_connection = mock.create_autospec(Connection)
        mock_task_on_pool = mock.create_autospec(TaskPool)

        # set the storage type to 0 to raise an error
        mock_connection.storage_type.pk = 0

        # set the target_connection for the task
        mock_task.target_connection = mock_connection

        # configure the task and pool action
        mock_task_on_pool.task = mock_task          
        mock_task_on_pool.action = Worker.ACTION_UPLOAD        

        # push the pool task to the queue
        task_pool.put(mock_task_on_pool)

        real = Worker(task_pool)
        real.item = task_pool.get()        

        error_occured = False
        try:
            real.upload()
        except Exception:
            error_occured = True
            
        self.assertTrue(error_occured)

    def test_worker_download_raise_available_storage_dont_exists(self):
        """ """
        task_pool = Queue(maxsize=0)

        # mocks
        mock_task = mock.create_autospec(Task)
        mock_connection = mock.create_autospec(Connection)
        mock_task_on_pool = mock.create_autospec(TaskPool)

        # set the storage type to 0 to raise an error
        mock_connection.storage_type.pk = 0

        # set the target_connection for the task
        mock_task.source_connection = mock_connection

        # configure the task and pool action
        mock_task_on_pool.task = mock_task          
        mock_task_on_pool.action = Worker.ACTION_UPLOAD        

        # push the pool task to the queue
        task_pool.put(mock_task_on_pool)

        real = Worker(task_pool)
        real.item = task_pool.get()        

        error_occured = False
        try:
            real.upload()
        except Exception:
            error_occured = True
            
        self.assertTrue(error_occured)

    def tst_notify_task_finished_ok(self):

        mock_worker = mock.create_autospec(Worker)
        mock_worker._queueitem.action = Worker.ACTION_DOWNLOAD

        mock_taskpool = mock.create_autospec(TaskPool)

        task_pool = Queue(maxsize=0)
        real = Worker(task_pool)

        real.notify_task_finished(None)

        print mock_taskpool.action


        
        


