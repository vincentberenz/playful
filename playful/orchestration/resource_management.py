# Copyright 2019 Max Planck Gesellschaft
# Author: Vincent Berenz



class fCommit:
    
    _commited = {} # id(component):end commitment
    _lock = threading.Lock()
    _last_time_commited = {} #id(component):time last time it was ucommited
    
    @classmethod
    def commit(cls,component):
        
        if not component.get_commit_duration():
            return 
        if id(component) in cls._commited :
            return
        
        with cls._lock: 
            can_commit = False
            try : 
                if time.time() > (cls._last_time_commited[id(component)]+0.5) :
                    can_commit=True
            except :
                can_commit = True
            if can_commit:
                cls._commited[id(component)]=time.time()+component.get_commit_duration()
                
    @classmethod
    def is_commited(cls,component):
        
        with cls._lock:
            if id(component) in list(cls._commited.keys()):
                if time.time()<cls._commited[id(component)]: return True
                cls._last_time_commited[id(component)]=time.time()
                del cls._commited[id(component)]
                
        return False

    
class fResources:
    
    _resources = [] # list of resources
    _using_resources = {} # resource : component that is using it
    _should_have_resource = {} # resource : component that has priority in using it
    _asked_for_resource = {} # component : [resources it want]
    _must_have_resource = {} # component : [resource it MUST GET NOW. Override everything]
    _lock = threading.Lock()
    _stopped = False
    
    @classmethod
    def get_resources(cls):
        return [r for r in cls._resources]

    @classmethod
    def stop(cls):
        with cls._lock:
            cls._stopped = True
            cls._should_have_resource = {r:[] for r in cls._resources}
            cls._asked_for_resource = {r:[] for r in cls._resources}
            
    @classmethod
    def report(cls):
        s = ["[resources]"]
        using = ["\tusing || \t"]
        for r,f in cls._using_resources.items():
            if f is not None : using.append(r+" : "+str(f))
        should_have = ["\tshould_have || \t"] 
        for r,f in cls._should_have_resource.items():
            if f is not None : should_have.append(r+" : "+str(f))
        s.append('\t'.join(using))
        s.append('\t'.join(should_have))
        return s
    
    @classmethod
    def _cleaning(cls,components):
        component_ids = [id(f) for f in components]
        for r,f in cls._using_resources.items() :
            if f not in component_ids: cls._using_resources[r]=None
        for r in cls._asked_for_resource: 
            old_list = cls._asked_for_resource[r]
            new_list = [f for f in old_list if f in component_ids]
            cls._asked_for_resource[r]=new_list
            
    @classmethod
    def _get_asked_resources(cls,component):
        asked = []
        for r,components_list in cls._asked_for_resource.items():
            if component in components_list : asked.append(r)
        return asked
    
    @classmethod
    def attribute_resources(cls,components):
        if not cls._stopped:
            with cls._lock:
                cls._cleaning(components)
                cls._should_have_resource = {r:None for r in cls._resources}
                available_resources = [r for r in cls._resources]
                # component which are commited for a certain duration
                for component in components:
                    if fCommit.is_commited(component):
                        asked_resources = cls._get_asked_resources(id(component))
                        for ar in asked_resources :
                            if ar in available_resources : 
                                cls._should_have_resource[ar]=id(component)
                                available_resources.remove(ar)
                # component which called "take_resource" must have them, independantly of the ordering
                for resource,component_id in cls._must_have_resource.items():
                    if resource in available_resources:
                        if component_id is not None:
                            cls._should_have_resource[resource]=component_id
                            available_resources.remove(resource)
                # for components which played fair and called "ask for resource"
                for f in components:
                    asked_resources = cls._get_asked_resources(id(f))
                    for ar in asked_resources :
                        if ar in available_resources : 
                            cls._should_have_resource[ar]=id(f)
                            available_resources.remove(ar)
                    if not available_resources : break



def untake_resource(component,resource):
    with fResources._lock:
        if fResources._must_have_resource[resource]==id(component):
            fResources._must_have_resource[resource]=None

def take_resource(component,resource):
    with fResources._lock:
        if resource not in fResources._resources :
            raise Exception(component.__class__.__name__+
                            " is asking for a resource that has not been registered: |"+
                            str(resource)+"| (known resources : "+
                            " ".join(["|"+str(r)+"|" for r in fResources._resources])+")")
        
        if (id(component) not in fResources._asked_for_resource[resource]) or (fResources._must_have_resource[resource] is None):
            fResources._asked_for_resource[resource].append(id(component)) 
            fResources._must_have_resource[resource]=id(component)
            
        if fResources._should_have_resource[resource]==id(component):
            if fResources._using_resources[resource] is None : 
                fResources._using_resources[resource] = id(component)
                return True
            elif fResources._using_resources[resource] == id(component):
                return True
            
        return False

def ask_for_resource(component,resource):
    with fResources._lock:
        if resource not in fResources._resources :
            raise Exception(component.__class__.__name__+
                            " is asking for a resource that has not been registered: |"+
                            str(resource)+"| (known resources : "+
                            " ".join(["|"+str(r)+"|" for r in fResources._resources])+")")
        
        if id(component) not in fResources._asked_for_resource[resource] :
            fResources._asked_for_resource[resource].append(id(component))
            
        if fResources._should_have_resource[resource]==id(component):
            
            if fResources._using_resources[resource] is None : 
                fResources._using_resources[resource] = id(component)
                return True
            elif fResources._using_resources[resource] == id(component):
                return True
            
        return False

def is_having_resource(component,resource):
    with fResources._lock: 
        if fResources._using_resources[resource] == component :
            return True
    return False

def stop_asking_for_resource(component,resource):
    with fResources._lock:
        try :
            fResources._asked_for_resource[resource].remove(id(component)) 
        except :
            pass
        try :
            if fResources._must_have_resource[resource]==id(component):
                fResources._must_have_resource[resource]=None
        except : pass

def release_resource(component,resource):
    with fResources._lock:
        if resource not in fResources._resources :
            raise Exception(component.__class__.__name__+" is releasing a resource that has not been registered :"+resource)
        if fResources._using_resources[resource]==id(component) :fResources._using_resources[resource]=None

def resources_used(component):
    with fResources._lock:
        return [r for r in fResources._resources if fResources._using_resources[r]==id(component)]
