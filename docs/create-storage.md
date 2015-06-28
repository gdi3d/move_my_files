# Creating a new storage

To create a new storage for **Move my files** follow this steps

1. Create a new app using `./manage.py startapp mynew_storage`
2. Inside **mynew_storage.models** create two models as mentioned on [classes to implement](#inside-mynew_storagemodels)
3. Add **mynew_storage** app to **INSTALLED_APPS** on **config.settings**
4. Start the development server `./manage.py runserver` and login to [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)
5. Go to **main > Available storages > add** and enter the name of your connection. In our example: **My New** and in the **configuration class name** field you should the enter the name of the class that holds the configuration for it, in our case **MyNewConnectionSettings** (this will be transform to lowercase after being saved)

If you don't make the changes specified on step 5 you won't be able to connect to the storage while runing the tasks


## Classes to implement
You need to implement two classes inside your models.py:

1. ***YourStorageName***Storage This will handle all the basic operations
2. ***YourStorageName***ConnectionSettings This will store the connection configuration

Notice that we use a suffix for each class **Storage** and **ConnectionSettings**. 
These are not mandatory but it's a convention to make the code more readable

### Storage Class

This class need to extend **main.models.AbstractStorage** and implement these methods:

* list_directory
* write_file
* read_file
* file_exists 

Example:

```
from main.models import AbstractStorage

class MyNewStorage(AbstractStorage):
    """ MyNew API Storage. """

    def __init__(self, user, password):
        """ Connect to the storage using proper credentials """
        self.conn = SomeConnection(user, password)        

    def list_directory(self, path):
    	""" Return the content of a directory as a list """
        pass

    def write_file(self, source_pathname, target_pathname = None):
        """ 
        Write the file on the storage and return response from
        the storage 
        """
        pass

    def read_file(self, pathname):
        """ Read the specified file and return it's handle. """
        pass        

    def file_exists(self, pathname):
        """ Check if the file exists """
        pass
```

### Connection Settings Class

This class has to extend **main.models.Connection** and implement one method:

* connect

Example:

```
from main.models import Connection
from main.exceptions import *

class MyNewConnectionSettings(Connection):
    """ MyNew model """
    # define your models fields here
    pass
    
    def __unicode__(self):
        pass
    
    def connect(self):
        if not hasattr(self, 'conn'):
            try:                
                self.conn = MyNewStorage(...)
            except:
                raise ConnectionFailed(_("Coundn't connect to MyNew: %s") % self.url)
```