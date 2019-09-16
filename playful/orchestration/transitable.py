# Copyright 2019 Max Planck Gesellschaft
# Author: Vincent Berenz


from ..interpreter.evaluation import Evaluation


class state_transition:

    
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

    
    def set_scheme_id_and_scheme_type(self,
                                      scheme_id,
                                      scheme_type):
        
        self._evaluation = Evaluation.read(self._evaluation_str,scheme_id,scheme_type,**self._kwargs)

        
    @staticmethod
    def read(s,**kwargs):
        
        if 'if' not in s:
            raise Exception( str("Could not understand the state transition "+
                                s+" : keyword 'if' missing"+" : "+str(s)) )
        if 'switch to' not in s:
            raise Exception(str("Could not understand the state transition "+
                                s+" : keyword 'switch to' missing : "+str(s)))
        
        state_name = s[s.index('switch to')+9:s.index('if')].strip()
        evaluation_str = s[s.index('if')+2:]
        
        return state_transition(state_name,evaluation_str,s,**kwargs)


    
class Transitable(object):

    
    def __init__(self, **kwargs):

        self._state_transitions = []
        self._next_state = None
        self._being_killed = False

        
    def get_errors(self):

        return []

    
    def get_next_state(self):

        return self._next_state

    
    def iterate(self, parent_run=False, kill=False):

        if not parent_run:
            return

        if kill:
            self._being_killed = True

        if self._being_killed:
            parent_run = False

        self._next_state = None

        for state_transition in self._state_transitions:
            next_state = state_transition.transit()
            if next_state is not None:
                self._next_state = next_state
                break
                
    def set_scheme_id_and_scheme_type(self, scheme_id, scheme_type):

        for st in self._state_transitions:
            st.set_scheme_id_and_scheme_type(scheme_id, scheme_type)

            
    def set_state_transition_strs(self, state_transitions_str, **kwargs):

        self._state_transitions = [state_transition.read(
            st, **kwargs) for st in state_transitions_str if st]
