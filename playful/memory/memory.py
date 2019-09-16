# Copyright 2019 Max Planck Gesellschaft
# Author: Vincent Berenz


import threading,copy,collections


class Memory :

    DEFAULT_ID=-1
    
    _lock = threading.Lock()
    items = {}
    key_values = {}
    new_instances = []
    deleted_instances = []


    @classmethod
    def reset(cls):
        cls._lock = threading.Lock()
        cls.items = {}
        cls.key_values = {}
        cls.new_instances = []
        cls.deleted_instances = []
    
    @classmethod
    def new_items(cls):
        with cls._lock:
            r = cls.new_instances
            cls.new_instances = []
            return r

        
    @classmethod
    def deleted_items(cls):
        with cls._lock:
            r = cls.deleted_instances
            cls.deleted_instances = []
            return r


    @classmethod
    def _set(cls,item,item_id=None):

        if item_id is None:
            item_id_ = Memory.DEFAULT_ID
        else:
            item_id_ = item_id
        item_id = None

        classname = item.__class__.__name__

        try :
            d = cls.items[classname]
        except :
            d = {}
            cls.items[classname]=d

        if item_id_ not in d.keys():
            cls.new_instances.append((classname,item_id_))
        d[item_id_] = copy.deepcopy(item)

        

    @classmethod
    def set(cls,item,item_id=None):

        with cls._lock:

            # we add an key/value item
            if item.__class__.__name__=="str":
                cls.key_values[item]=item_id
                return

            # we add an instance object item
            item_id_ = item_id
            item_id = None
            cls._set(item,item_id=item_id_)

            
    @classmethod
    def delete(cls,classname,item_id=None):

        with cls._lock:

            if item_id is None:
                item_id_ = Memory.DEFAULT_ID
            else :
                item_id_ = item_id
            item_id = None

            try :
                del cls.items[classname][item_id_]
                cls.deleted_instances.append((classname,item_id_))
            except Exception as e:
                pass
        

    @classmethod
    def _get(cls,classname,item_id=None):
        
        if item_id is None:
            item_id_ = Memory.DEFAULT_ID
        else :
            item_id_ = item_id
        item_id = None

        try :
            return copy.deepcopy( cls.items[classname][item_id_] )
        except :
            return None

        
    @classmethod
    def get(cls,classname,item_id=None):

        with cls._lock:

            # we retrieve a key/value item
            if classname in cls.key_values.keys():
                return cls.key_values[classname]

            # we retrieve a class instance item
            item_id_ = item_id
            item_id = None
            return cls._get(classname,item_id=item_id_)


    @classmethod
    def setattr( cls,
                 classname,
                 attr,
                 value,
                 item_id=None):

        with cls._lock:
            if item_id is None:
                item_id_ = cls.DEFAULT_ID
            else :
                item_id_ = item_id
            item_id = None
            item = cls._get(classname,item_id=item_id_)
            if item is None:
                return False
            setattr(item,attr,copy.deepcopy(value))
            cls._set(item,item_id_)
            return True


            
    @classmethod
    def get_all(cls,classname):

        with cls._lock:

            try :
                d = cls.items[classname]
            except :
                return None

            return { item_id:copy.deepcopy(item)
                     for item_id,item in d.items() }
