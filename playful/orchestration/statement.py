# Copyright 2019 Max Planck Gesellschaft
# Author: Vincent Berenz


import collections,time
from .behavior_container import Behaviors_container
from .state_container import State_container
from .evaluable import Evaluable
from .scoreable import Scoreable
from .transitable import Transitable
from ..component.component import Component


class Statement(
        Behaviors_container,
        Transitable,
        State_container,
        Evaluable,
        Scoreable):

    
    def __init__(self, **kwargs):

        self.name = None
        self._should_stop = True
        self._scheme_id = None
        self._scheme_type = None
        self._errors = []

        self._super = [
            Behaviors_container,
            Transitable,
            State_container,
            Evaluable,
            Scoreable]

        self._iterate_super = [
            Behaviors_container,
            Transitable,
            State_container]

        for super_ in self._super:
            super_.__init__(self, **kwargs)

        self._frequency_queue = collections.deque(
            [time.time() for _ in range(10)], 10)

        self._frequency = 0
        self._being_killed = False

        
    def is_running(self):

        r = Behaviors_container.is_running(
            self) or State_container.is_running(self)
        return r

    
    def _set_name(self, name):

        self.name = name

        
    def get_errors(self):

        if self._errors:
            return self._errors
        for super_ in self._super:
            self._errors.extend(super_.get_errors(self))
        return self._errors

    
    def iterate(self, parent_run=False, kill=False):

        if kill:
            self._being_killed = True

        if self._being_killed:
            parent_run = False

        if self._errors:
            parent_run = False

        if parent_run:
            self._frequency_queue.append(time.time())
            self._frequency = 10.0 / \
                (self._frequency_queue[-1] - self._frequency_queue[0])
            if (not self.evaluable_evaluate()) or float(self) < 0:
                parent_run = False
        else:
            self._frequency = 0

        for super_ in self._iterate_super:
            super_.iterate(self, parent_run=parent_run, kill=kill)

            
    def tree_string_representation(self, all_nodes=[]):

        sub_fractales = Behaviors_container.get_behaviors(self)
        active_state = State_container.get_active_state(self)

        if active_state:
            sub_fractales.append(active_state)

        scheme_id_str = ""

        if self._scheme_id:
            scheme_id_str = "-" + str(self._scheme_id)

        r = [str(id(self)) + scheme_id_str]

        for sf in sub_fractales:
            r.append(str(id(sf)))

        all_nodes.append(r)

        for sf in sub_fractales:
            sf.tree_string_representation(all_nodes=all_nodes)

        return "|".join([str(n) for n in all_nodes])

    
    def introspection(self, activated_components=[]):

        sub_fractales = Behaviors_container.get_behaviors(self)
        active_state = State_container.get_active_state(self)

        if active_state:
            sub_fractales.append(active_state)

        for sf in sub_fractales:
            sf.introspection(activated_components=activated_components)

            
    def report(self, tab=''):

        sub_fractales = Behaviors_container.get_behaviors(self)
        active_state = State_container.get_active_state(self)

        if active_state:
            sub_fractales.append(active_state)

        # we display in report only score>0
        score = float(self.get_score())

        if score > 0:
            r = [
                tab +
                "|" +
                "{:.2f}".format(score) +
                "| " +
                self.name +
                " (" +
                "{:.2f}".format(
                    self._frequency) +
                "HZ)"]
            sub_fractales.sort(reverse=True)
            for sf in sub_fractales:
                r.extend(sf.report(tab=tab + '\t'))
        else:
            r = []

        return r

    
    def manage_template_behaviors_instances(
            self, new_schemes, deleted_schemes):

        for super_ in [Behaviors_container, State_container]:
            super_.manage_template_behaviors_instances(
                self, new_schemes, deleted_schemes)

            
    def set_scheme_id_and_scheme_type(self, scheme_id, scheme_type):

        for super_ in self._super:
            super_.set_scheme_id_and_scheme_type(self, scheme_id, scheme_type)

            
    def get_scheme_id(self):
        return self._scheme_id


    def get_scheme_type(self):
        return self._scheme_type

    
    def get_ordered_components(self):

        sub_fractales = Behaviors_container.get_behaviors(self)
        active_state = State_container.get_active_state(self)

        if active_state:
            sub_fractales.append(active_state)
        sub_fractales.sort(reverse=True)

        components = []

        for sf in sub_fractales:
            if isinstance(sf, Component):
                components.append(sf)
            else:
                components.extend(sf.get_ordered_components())

        return components
