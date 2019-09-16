# Copyright 2019 Max Planck Gesellschaft
# Author: Vincent Berenz


import threading,traceback
from ..interpreter.evaluation import Evaluation

class Evaluable(object):

    
    def __init__(self, **kwargs):

        self._evaluation_str = None
        self._evaluation_kwargs = kwargs
        self._scheme_id = None
        self._scheme_type = None
        self._lock = threading.Lock()
        self._e_value = False
        self._e_errors = []
        self.__nonzero__ = self.__bool__
        
    def get_errors(self):
        
        return self._e_errors

    
    def evaluable_evaluate(self):
        return self.__bool__()

    
    def set_evaluation_str(self, evaluation_str, **evaluation_kwargs):

        self._evaluation_str = evaluation_str
        self._evaluation_kwargs = evaluation_kwargs

        
    def set_scheme_id_and_scheme_type(self, scheme_id, scheme_type):

        self._scheme_id = scheme_id
        self._scheme_type = scheme_type
        if self._evaluation_str:
            self._evaluation = Evaluation.read(
                self._evaluation_str,
                scheme_id,
                scheme_type,
                **self._evaluation_kwargs)
        else:
            self._evaluation = True

            
            
    def __bool__(self):

        with self._lock:

            self._e_value = False

            if not self._e_errors:
                try:
                    if self._evaluation:
                        self._e_value = True
                except Exception as e:
                    trace = traceback.format_exc().splitlines()
                    error = "\n".join(trace[-3:])
                    self._e_errors.append( str("exception thrown in "+
                                               self._evaluation_str+":\n"+
                                               str(error)) )

            return self._e_value
