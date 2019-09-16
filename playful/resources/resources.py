# Copyright 2019 Max Planck Gesellschaft
# Author: Vincent Berenz


import threading


class Resources:

    
    _resources = set()  # list of resources
    _using_resources = {}  # resource : component that is using it
    _should_have_resource = {}  # resource : component that has priority in using it
    _asked_for_resource = {}  # resources : [components that want it]
    _must_have_resource = {} # component : [resource it MUST GET NOW. Override everything]

    _lock = threading.Lock()
    _stopped = False

    @classmethod
    def reset(cls):
        cls._resources = set()
        cls._using_resources = {}
        cls._should_have_resource = {}
        cls._ask_for_resource = {}
        cls.must_have_resource = {}
        cls._lock = threading.Lock()
        cls._stopped = False
    

    @classmethod
    def add_resource(cls,resource):
        contained = resource in cls._resources
        if not contained:
            cls._resources.add(resource)
            cls._using_resources[resource]=None
            cls._should_have_resource[resource]=[]
            cls._asked_for_resource[resource]=[]
    
    @classmethod
    def get_resources(cls):
        return [r for r in cls._resources]

    
    @classmethod
    def stop(cls):

        with cls._lock:
            cls._stopped = True
            cls._should_have_resource = {r: [] for r in cls._resources}
            cls._asked_for_resource = {r: [] for r in cls._resources}

            
    @classmethod
    def report(cls):

        s = ["[resources]"]
        using = ["\tusing || \t"]

        for r, f in cls._using_resources.items():
            if f is not None:
                using.append(r + " : " + str(f))

        should_have = ["\tshould_have || \t"]

        for r, f in cls._should_have_resource.items():
            if f is not None:
                should_have.append(r + " : " + str(f))
                
        s.append('\t'.join(using))
        s.append('\t'.join(should_have))

        return s

    
    @classmethod
    def _cleaning(cls, components):

        component_ids = [id(f) for f in components]

        for r, f in cls._using_resources.items():
            if f not in component_ids:
                cls._using_resources[r] = None

        for r in cls._asked_for_resource:
            old_list = cls._asked_for_resource[r]
            new_list = [f for f in old_list if f in component_ids]
            cls._asked_for_resource[r] = new_list

            
    @classmethod
    def _get_asked_resources(cls, component):

        asked = []

        for r, components_list in cls._asked_for_resource.items():
            if component in components_list:
                asked.append(r)

        return asked

    
    @classmethod
    def attribute_resources(cls, components):

        if not cls._stopped:

            with cls._lock:

                cls._cleaning(components)
                cls._should_have_resource = {r: None for r in cls._resources}

                available_resources = [r for r in cls._resources]

                # component which called "take_resource" must have them,
                # independantly of the ordering
                for resource, component_id in cls._must_have_resource.items():
                    if resource in available_resources:
                        if component_id is not None:
                            cls._should_have_resource[resource] = component_id
                            available_resources.remove(resource)
                            
                # for components which played fair and called "ask for
                # resource"
                for f in components:
                    asked_resources = cls._get_asked_resources(id(f))
                    for ar in asked_resources:
                        if ar in available_resources:
                            cls._should_have_resource[ar] = id(f)
                            available_resources.remove(ar)
                    if not available_resources:
                        break



