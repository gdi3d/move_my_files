"""
This file should be runing as a deamon on your system
It will pull task from the pool every 20 seconds
after one or more workers are free to handle a task
"""

from django.conf import settings
from Queue import Queue
from main.models import Worker
from queue.models import TaskPool

import time
from datetime import datetime


def run():

    SLEEP_INTERVAL = 20

    print "I'm ready to go..."

    q = Queue(maxsize=0)
    
    max_workers = 5

    for i in range(max_workers):
        worker = Worker(q)
        worker.setDaemon(True)
        worker.start()
  
    while True:
        pool = TaskPool.objects.filter(status=TaskPool.STATUS_QUEUED)
        
        if settings.DEBUG:
            print 'Getting task from pool... %s' % datetime.now()
            if pool:
                print pool        
            else:
                print 'Nothing in the pool yet...'

        for t in pool:
            t.status = TaskPool.STATUS_RUNING
            t.save()
            q.put(t)

        q.join()

        if settings.DEBUG:
            print 'Waiting %s seconds..' % SLEEP_INTERVAL

        time.sleep(SLEEP_INTERVAL)
    
    
