# Interface

To create a new storage for **Move my files** you need to implement two models:

1. ***YourStorageName***Storage
2. ***YourStorageName***ConnectionSettings

## Storage Class

Empty class:

```
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

    def file_exists(self, pathname):
        """ Check if the file exists """
```

### Connection Settings Class

```
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