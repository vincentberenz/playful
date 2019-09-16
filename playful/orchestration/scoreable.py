# Copyright 2019 Max Planck Gesellschaft
# Author: Vincent Berenz


import threading,traceback
from ..interpreter.score_calculator import Score_calculator_str


class Scoreable(object):
    
    def __init__(self, **kwargs):

        self._score_calculators_str = None
        self._score = 1
        self._lock = threading.Lock()
        self._score_calculators = None
        self._scheme_id = None
        self._scheme_type = None
        self._sa_errors = []

        
    def get_errors(self):

        return self._sa_errors

    
    def set_score_calculator_strs(self, score_calculators_str, **kwargs):

        self._score_calculators_str = [Score_calculator_str.read(
            sc, **kwargs) for sc in score_calculators_str if sc]

        
    def __lt__(self, other):

        return self._score < other._score

    
    def set_scheme_id_and_scheme_type(self, scheme_id, scheme_type):

        self._scheme_id = scheme_id
        self._scheme_type = scheme_type
        if self._score_calculators_str is not None:
            self._score_calculators = [
                s.get_score_calculator(
                    scheme_id,
                    scheme_type) for s in self._score_calculators_str if s is not None]
        else:
            self._score_calculators = []

            
    def get_score(self):

        with self._lock:
            return self._score


    def scoreable_evaluate(self):

        return self.__float__()

    
    def __float__(self):

        with self._lock:

            if not self._sa_errors:
                for score_c in self._score_calculators:
                    if score_c:
                        try:
                            self._score = float(score_c)
                        except Exception as e:
                            trace = traceback.format_exc().splitlines()
                            error = "\n".join(trace[-3:])
                            self._sa_errors.append( str("exception thrown in "+
                                                       self._evaluation_str+":\n"+
                                                       str(error)) )
                        break
                    else:
                        self._score = 0.0

            else:
                self._score = 0.0

        return float(self._score)
