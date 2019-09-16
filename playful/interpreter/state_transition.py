# Copyright 2019 Max Planck Gesellschaft
# Author: Vincent Berenz



from .evaluation import Evaluation

class State_transition:
    
    def __init__( self,
                  state_name,
                  evaluation_str,
                  original,
                  **kwargs):
        
        self._state_name,self._evaluation_str,self._original,self._kwargs = state_name,evaluation_str,original,kwargs
        
    def __str__(self):
        return self._original
    
    def transit(self):
        if self._evaluation:
            return self._state_name
        return None
    
    def set_scheme_id_and_scheme_type(self,scheme_id,scheme_type):
        self._evaluation = Evaluation.read( self._evaluation_str,
                                            scheme_id,
                                            scheme_type,
                                            **self._kwargs )
        
    @staticmethod
    def read(s,**kwargs):
        if 'if' not in s:
            raise Exception("Could not understand the state transition "+
                            s+" : keyword 'if' missing"+" : "+str(s))
        if 'switch to' not in s:
            raise Exception("Could not understand the state transition "+
                            s+" : keyword 'switch to' missing : "+str(s))
        state_name = s[s.index('switch to')+9:s.index('if')].strip()
        evaluation_str = s[s.index('if')+2:]
        return State_transition(state_name,evaluation_str,s,**kwargs)
