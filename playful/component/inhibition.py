# Copyright 2019 Max Planck Gesellschaft
# Author: Vincent Berenz


class Inhibition(object):
    
    _inhibited = {}
    _lock = threading.Lock()
    
    @classmethod
    def set(cls,component_name,inhib):
        with cls._lock:
            cls._inhibited[component_name]=inhib
            
    @classmethod
    def is_inhibited(cls,component_name):
        with cls._lock:
            try : return cls._inhibited[component_name]
            except : return False
