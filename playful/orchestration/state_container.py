# Copyright 2019 Max Planck Gesellschaft
# Author: Vincent Berenz


class State_container(object):

    
    def __init__(self, **kwargs):

        self._sub_states = {}
        self._starting_sub_state = None
        self._next_sub_state = None
        self._active_sub_state = None
        self._sc_errors = []
        self._state_transition_error = None
        self._being_killed = False

        
    def get_errors(self):

        if self._sc_errors:
            return self._sc_errors

        for _, sub_state in self._sub_states.items():
            self._sc_errors.extend(sub_state.get_errors())

        if self._state_transition_error:
            self._sc_errors.append(self._state_transition_error)

        return self._sc_errors

    
    def get_active_state(self):

        return self._active_sub_state

    
    def iterate(self, parent_run=False, kill=False):

        if kill:
            self._being_killed = True

        if self._being_killed:
            parent_run = False

        if parent_run:
            self._manage_transitions()

        if self._active_sub_state is None and self._starting_sub_state:
            self._active_sub_state = self._sub_states[self._starting_sub_state]

        if self._active_sub_state is not None:
            self._active_sub_state.iterate(parent_run=parent_run)

            
    def is_running(self):

        if self._active_sub_state is not None:
            self._active_sub_state.is_running()

            
    def set_scheme_id_and_scheme_type(self, scheme_id, scheme_type):

        pass

    
    def _manage_transitions(self):

        if self._state_transition_error:
            return

        if self._active_sub_state is not None:

            if self._active_sub_state is not None:
                self._active_sub_state._manage_transitions()

            try:
                self._next_sub_state = self._active_sub_state.get_next_state()
                #print("\nstate container: ",self._next_sub_state)
            except Exception as e:
                trace = traceback.format_exc()
                self._state_transition_error.append(
                    trace +
                    "\nexecution error (state transition) : " +
                    self.name +
                    " " +
                    str(e) +
                    "\n")

            if self._next_sub_state is None:
                return
            
            if self._next_sub_state not in self._sub_states:
                self._error = "can not transit to " + \
                    str(self._next_sub_state) + " : no such state"
                self._next_sub_state = None
                return
            
            #self._active_sub_state.iterate(parent_run=True,kill=True)
            self._active_sub_state = self._sub_states[self._next_sub_state]
            self._next_sub_state = None

            
            
    def manage_template_behaviors_instances(
            self, new_schemes, deleted_schemes):

        for sub_state in list(self._sub_states.values()):
            sub_state.manage_template_behaviors_instances(
                new_schemes, deleted_schemes)

            
    def add_state(self, state):

        if not self._starting_sub_state:
            self._starting_sub_state = state.name
        self._sub_states[state.name] = state
