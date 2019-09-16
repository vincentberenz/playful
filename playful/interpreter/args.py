# Copyright 2019 Max Planck Gesellschaft
# Author: Vincent Berenz

import inspect,collections

# using signature in python2.7
try :
     import funcsigs
except :
     pass
     
def _get(instance):
     try :
          s = inspect.signature(instance)
          parameters = [p for p in s.parameters.values() if p.default != inspect._empty]
     except :
          s = funcsigs.signature(instance)
          parameters = [p for p in s.parameters.values() if p.default != funcsigs._empty]
     return [p.name for p in parameters],[p.default for p in parameters]

def get_args_dict(callable_,**kwargs):
    
    must_create_instance = False
    args_names = []
    default_values = []
    
    if inspect.isclass(callable_):
        
        must_create_instance = True
        try :
            args_names,default_values = _get(callable_.__init__)
        except :
            args_names,default_values = _get(callable_.__call__) # if singleton
            
    else :
        args_names,default_values = _get(callable_) 
            
    if len(args_names)!=len(default_values):
        raise Exception("Error while processing : "+
                        callable_.__class__.__name__+
                        " : non-default arguments are not allowed in robot-talk")
    
    args = {a:d for a,d in zip(args_names,default_values)}
    
    for a in kwargs:
        if a in args :
            args[a]=kwargs[a]

    return must_create_instance,args
