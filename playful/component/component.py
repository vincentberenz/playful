# Copyright 2019 Max Planck Gesellschaft
# Author: Vincent Berenz


import collections,time,threading,traceback

from ..orchestration.evaluable import Evaluable
from ..orchestration.scoreable import Scoreable
from ..orchestration.transitable import Transitable

from .resources_manager import Resources_manager
from .spineable import Spineable
from .memory_getter import Memory_getter
from ..resources.resources import Resources
from ..memory.memory import Memory


class Component(
        Evaluable,
        Transitable,
        Scoreable,
        Resources_manager,
        Spineable,
        Memory_getter):

    
    _EVAL_TIME = 0.04

    
    # __new__ method rather than __init__ is used so that creators of new
    # components do not need to call the constructor of the superclasses
    
    def __new__(self, **args):
        
        f = object.__new__(self)
        f.name = None
        f._should_pause = True
        f._should_stop = True
        f._errors = []
        f._scheme_id = None
        f._frequency_queue = collections.deque(
            [time.time() for _ in range(10)], 10)
        f._frequency = 0
        f._scheme_deleted = False
        f._being_killed = False
        f._inhibited = False

        Evaluable.__init__(f, **args)
        Scoreable.__init__(f, **args)
        Transitable.__init__(f)
        Resources_manager.__init__(f)
        Spineable.__init__(f)
        Memory_getter.__init__(f)

        for arg, value in args.items():
            setattr(f, arg, value)

        return f

    
    def kill(self):
        
        print(
            "kill signal received for component " +
            self.name +
            ", but " +
            self.name +
            " is not killable ...")

        
    def manage_template_behaviors_instances(
            self, new_schemes, deleted_schemes):
        
        if self._scheme_id:
            if self._scheme_id in [ds[1] for ds in deleted_schemes]:
                self._scheme_deleted = True

                
    def iterate(self, parent_run=False, kill=False):

        if kill:
            self._being_killed = True
            
        if self._being_killed:
            parent_run = False

        if parent_run:

            # float(self) and (not self) referes to bool and float
            # evaluations of super parents Evaluable and Scoreable
            if self._scheme_deleted or self.scoreable_evaluate() < 0 or not self.evaluable_evaluate():
                parent_run = False
                
        if not parent_run:
            self._should_pause = True
            self._should_stop = True
            self._frequency = 0
            
        else:
            self._frequency_queue.append(time.time())
            self._frequency = 10.0 / \
                (self._frequency_queue[-1] - self._frequency_queue[0])
            self._should_pause = False
            if not hasattr(self, '_t') or not self._t.isAlive():
                self._t = threading.Thread(target=self._execute)
                self._t.setDaemon(True)
                self._t.start()

        Transitable.iterate(self, parent_run=parent_run)

        
    def _set_name(self, name):
        self.name = name

        
    def _manage_transitions(self):
        pass

    
    def get_errors(self):

        if self._errors:
            return self._errors
        for s in [Evaluable, Scoreable, Transitable]:
            self._errors.extend(s.get_errors(self))
        return self._errors

    
    def __str__(self):

        return self.__class__.__name__

    
    def tree_string_representation(self, all_nodes=[]):
        
        scheme_id_str = ""
        if self._scheme_id:
            scheme_id_str = "-" + str(self._scheme_id)
        if self.is_running():
            all_nodes.append(["*" + str(id(self)) + scheme_id_str])
        else:
            all_nodes.append([str(id(self)) + scheme_id_str])

            
    def introspection(self, activated_components=[]):

        if self.is_running():
            activated_components.append(self.name)

            
    def report(self, tab=""):
        
        running = '[running]'
        should_pause = ''
        evaluated = ''
        denied = ''
        frequency = "(" + "{:.2f}".format(self._frequency) + "/" + \
            "{:.2f}".format(Spineable.get_frequency(self)) + "HZ)"
        targeting = ''
        if len(self._denied_resources) != 0:
            denied = "[denied resources : " + \
                ' '.join(self._denied_resources) + ']'
        used = ''
        used_resources = self.used_resources()
        if used_resources:
            used = "[resources: " + ' '.join(used_resources) + ']'
        if not self.is_running():
            running = ''
            if self._inhibited:
                should_pause = "[inhibited]"
        elif self.should_pause():
            should_pause = '[should pause]'
        if not self._e_value:
            evaluated = '[evaluated false]'
        if self._scheme_type:
            targeting = 'targeting:' + str(self._scheme_type) + '\t'
        score = self.get_score()
        
        return [tab +
                '|' +
                "{:.2f}".format(self.get_score()) +
                '| ' +
                targeting +
                self.name +
                ' (' +
                str(id(self)) +
                ') ' +
                frequency +
                running +
                should_pause +
                evaluated +
                denied +
                used]


    def is_inhibited(self):
        
        if fInhibition.is_inhibited(self.name):
            return True
        return False

    
    def should_pause(self):
        
        return self._should_pause

    
    def is_running(self):

        try:
            return self._t.isAlive()
        except BaseException:
            return False

        
    def set_scheme_id_and_scheme_type(self, scheme_id, scheme_type):
        
        self._scheme_id = scheme_id
        Evaluable.set_scheme_id_and_scheme_type(self, scheme_id, scheme_type)
        Scoreable.set_scheme_id_and_scheme_type(self, scheme_id, scheme_type)
        Memory_getter.set_scheme_id_and_scheme_type(
            self, scheme_id, scheme_type)
        Transitable.set_scheme_id_and_scheme_type(self, scheme_id, scheme_type)


    def get_target_id(self):
        return self.get_scheme_id()

    def get_target_class(self):
        return self._scheme_type

    def get_target(self):
        return Memory.get(self._scheme_type,
                          self._scheme_id)
        
    def get_scheme_id(self):
        return self._scheme_id

    def _execute(self):
        
        if not self._errors:

            class free_resources:
                def __init__(
                    self, component_instance): self.component_instance = component_instance

                def __enter__(self): pass

                def __exit__(self, t, value, traceback):
                    Resources_manager.reset(self.component_instance)
                    Spineable.reset(self.component_instance)
                    
            with free_resources(self):

                try:
                    if not self._errors:
                        self.execute()
                        
                except Exception as e:
                    Memory.set("error", self.__class__.__name__)
                    if not hasattr(self, '_error_lock'):
                        self._error_lock = threading.Lock()
                    with self._error_lock:
                        Memory.set("error", self.__class__.__name__)
                        Memory.set("error_message", str(e))
                        error = "fComponent execution error : " + \
                            self.__class__.__name__ + " " + str(e) + "\n"
                        error += traceback.format_exc()
                        self._should_pause = True
                        self._errors.append(error)

                        
    def execute(self):
        pass

    @staticmethod
    def pulled():
        return []

    @staticmethod
    def pushed():
        return []
