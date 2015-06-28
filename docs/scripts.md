# Scripts to run
There are two script that you should be calling to make **Move my files** work

* [scripts/deamon.py](#deamonpy)
* [scripts/scheduler.py](#schedulerpy)

### deamon.py
This will fetch all the task availables from the task pool 
**queue.models.TaskPool**.

By default it will only handle 5 tasks in parallel, but you can change it by
altering the value of the var **max_workers** inside the script

This script should be runing on the background.

Run it using: `./manage.py runscript deamon`

### scheduler.py
This script will be the responsible for adding task to the task pool 
**queue.models.TaskPool** by evaluating the scheduler configuration setted for
each task

This script should be called by your OS scheduler every minute

Run it using: `./manage.py runscript scheduler` 