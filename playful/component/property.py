# Copyright 2019 Max Planck Gesellschaft
# Author: Vincent Berenz


class Property(object):

    _extensions = {}

    def __init__(self,value=None):
        self._value = value
        self._lock = threading.Lock()
        self.__nonzero__ = self.bool
        
    @classmethod
    def extension(cls,method):
        cls._extensions[method.__name__]=method
        return method
    
    def __str__(self):
        return self.__class__.__name__+":"+str(self._value)

    def type(self):
        return self.__class__.__name__

    def get_value(self):
        return self._value,self._lock

    def get_value_copy(self):
        with self._lock :
            return copy.deepcopy(self._value)

    def set_value(self,value): 
        with self._lock : self._value = value

    def update(self,**kwargs):
        with self._lock :
            if self._value is not None:
                self._value.update(**kwargs)

    def similarity(self,other_property_value):
        return None
    
    def fuse(self,value):
        self.set_value(value)

    def __float__(self) :
        with self._lock :
            return float(self._value)
        
    def __bool__(self):
        with self._lock :
            return bool(self._value)

    def evaluate(self):
        try : return float(self)
        except : return bool(self)
        
    def get_extension_value(self,extension_name,**kwargs):
        try : _callable = getattr(self,extension_name)
        except : raise Exception("Property "+
                                 self.__class__.__name__+
                                 " does not have extension "
                                 +str(extension_name))
        return _callable(**kwargs)
    
    def get_pointer_to_extension(self,extension_name):
        try :
            return getattr(self,extension_name)
        except :
            raise Exception("Property "+
                            self.__class__.__name__+
                            " does not have extension "+str(extension_name))
