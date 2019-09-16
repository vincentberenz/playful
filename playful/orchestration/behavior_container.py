# Copyright 2019 Max Planck Gesellschaft
# Author: Vincent Berenz


import traceback

class Behaviors_container:

    def __init__(self, **kwargs):

        self._template_behaviors = {}
        self._behaviors = []
        self._running = False
        self._scheme_id_to_delete = []
        self._kwargs = kwargs
        self._b_errors = []
        self._treated_scheme_ids = []
        self._being_killed = False

        
    def get_errors(self):

        if self._b_errors:
            return self._b_errors
        for b in self._behaviors:
            self._b_errors.extend(b.get_errors())
        return self._b_errors

    
    def is_running(self):

        if any([b.is_running() for b in self._behaviors]):
            return True

        return False

    
    def manage_template_behaviors_instances(
            self, new_schemes, deleted_schemes):

        # creating new behavior based on template if required
        if new_schemes:
            for scheme_type, scheme_id in new_schemes:
                if scheme_type in self._template_behaviors:
                    if scheme_id not in self._treated_scheme_ids:
                        for _, instantiable_fractal in self._template_behaviors[scheme_type]:
                            try:
                                fractal = instantiable_fractal.instantiate(
                                    scheme_type, scheme_id)
                                self._behaviors.append(fractal)
                            except Exception as e:
                                self._b_errors.append(
                                    str(e) + '\n' + traceback.format_exc())
                self._treated_scheme_ids.append(scheme_id)

        # deleting instances of template behaviors if required
        if deleted_schemes:
            behaviors_to_stop = [
                b for b in self._behaviors if b.get_scheme_id() in deleted_schemes]
            self._scheme_id_to_delete.extend(
                [b.get_scheme_id() for b in behaviors_to_stop])
            for b in behaviors_to_stop:
                b.iterate(parent_run=False, kill=True)

        # some behaviors were being deleted, but not yet stopped. monitoring
        # that
        if self._scheme_id_to_delete:
            to_delete = {}
            being_deleted = [
                b for b in self._behaviors if b.get_scheme_id() in self._scheme_id_to_delete]
            for b in being_deleted:
                try:
                    to_delete[b.get_scheme_id()].append(b)
                except BaseException:
                    to_delete[b.get_scheme_id()] = [b]
            for scheme_id, behaviors in to_delete.items():
                if not any([b.is_running() for b in behaviors]):
                    self._scheme_id_to_delete.remove(scheme_id)
                    for b in behaviors:
                        self._behaviors.remove(b)
                        del(b)
                        
        for b in self._behaviors:
            b.manage_template_behaviors_instances(new_schemes, deleted_schemes)

            
    def get_behaviors(self):
        return [b for b in self._behaviors]

    
    def iterate(self, parent_run=False, kill=False):

        if kill:
            self._being_killed = True

        if self._being_killed:
            parent_run = False

        for b in self._behaviors:
            b.iterate(parent_run=parent_run)

            
    def add_targeted_behavior(
            self, behavior_name, target, instantiable_fractal):

        if target not in self._template_behaviors:
            self._template_behaviors[target] = [
                (behavior_name, instantiable_fractal)]

        else:
            self._template_behaviors[target].append(
                (behavior_name, instantiable_fractal))

            
    def add_behavior(self, behavior):

        self._behaviors.append(behavior)
        
    def set_scheme_id_and_scheme_type(self, scheme_id, scheme_type):

        pass
