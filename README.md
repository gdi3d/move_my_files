# Move My Files (on beta state)

## Why use this?
You manage a few servers for some clients. Those clients have, on  regular basis, backups tasks and they store their backups on different services like S3, FTP, Dropbox, etc.

For each client you would have to setup scripts to transfer those files from the source to remote backups servers.

## How?
Centralizate all your **mv** operations on one place.

1. Setup the conections credentials for the source and remote servers
2. Create a the task setting the source and remote connection to use and what files (/some/path/to/file.tar.gz or /some/path/to/*)
3. Schedule that task.


# Install
I would recommend to install it using [Virtual Environments](http://docs.python-guide.org/en/latest/dev/virtualenvs/) (and [virtualenvwrapper](http://docs.python-guide.org/en/latest/dev/virtualenvs/#virtualenvwrapper) that provides autocomplete features).  

Install:
```
mkvirtualenv move_my_files
workon move_my_files
mkdir move_my_files
cd move_my_files
git clone https://github.com/gdi3d/move_my_files.git .
pip install -r requirements.txt
./manage.py runserver
```
Now open your browser at:

[http://127.0.0.1:8000/admin](http://127.0.0.1:8000/admin) and login using:

**username:** admin  
**password:** admin

### Misc
S3 and Dropbox storage base files were taken from https://github.com/nimbis/django-dbbackup