"""
This file should be trigger on a cronjob
to run every minute.
He's responsability is to check if any tasks
should be add the to the pool by the rules of
the scheduler configuration
"""

from django.conf import settings
from main.models import Scheduler, Worker
from queue.models import TaskPool
from pytz import timezone

import datetime

def run():
    
    now = datetime.datetime.now().replace(tzinfo=timezone(settings.TIME_ZONE))
    
    # get all scheduler avaibles
    for s in Scheduler.objects.task_availabes():        
        
        # check if the pool is empty
        # and create the first task if needed
        pool = TaskPool.objects.filter(task = s.task)

        if not pool:
            s.task.add_to_pool()
        elif s.recurrent:
            # check if the task in the scheduler
            # should be added to the task pool
            if s.repeat_interval_type == Scheduler.INTERVAL_TYPE_HOURS:
                minutes_interval = 60*s.repeat_interval
            elif s.repeat_interval_type == Scheduler.INTERVAL_TYPE_DAYS:
                minutes_interval = 60*24*s.repeat_interval
            else:
                minutes_interval = s.repeat_interval

            # get the all latests the finished tasks
            # this should be using group by task
            # but i can't make it work on sqlite for some reason
            pool = TaskPool.objects.filter(task = s.task, status = TaskPool.STATUS_FINISH, action=Worker.ACTION_UPLOAD).order_by('-modified')
            
            # ugly hack to fix missing group by
            task_checked = list()
            for p in pool:                
                # ugly hack to fix missing group by
                if s.task.id not in task_checked:
                    # when this task should run again?
                    next_run = p.modified.astimezone(timezone(settings.TIME_ZONE)) + datetime.timedelta(minutes = minutes_interval)

                    if next_run <= now.astimezone(timezone(settings.TIME_ZONE)):                        
                        s.task.add_to_pool()

                    task_checked.append(s.task.id)                    