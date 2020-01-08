# Copyright 2019 Max Planck Gesellschaft
# Author: Vincent Berenz


from ..resources.resources import Resources
import time


def untake_resource(component,resource):
    with Resources._lock:
        if Resources._must_have_resource[resource]==id(component):
            Resources._must_have_resource[resource]=None

            
def take_resource(component,resource):
    with Resources._lock:
        Resources.add_resource(resource)
        if ( (id(component) not in Resources._asked_for_resource[resource])
             or (Resources._must_have_resource[resource] is None) ):
            Resources._asked_for_resource[resource].append(id(component)) 
            Resources._must_have_resource[resource]=id(component)
        if Resources._should_have_resource[resource]==id(component):
            if Resources._using_resources[resource] is None : 
                Resources._using_resources[resource] = id(component)
                return True
            elif Resources._using_resources[resource] == id(component):
                return True
        return False

    
def ask_for_resource(component,resource):
    with Resources._lock:
        Resources.add_resource(resource)
        if id(component) not in Resources._asked_for_resource[resource] :
            Resources._asked_for_resource[resource].append(id(component)) 
        if Resources._should_have_resource[resource]==id(component):
            if Resources._using_resources[resource] is None :
                Resources._using_resources[resource] = id(component)
                return True
            elif Resources._using_resources[resource] == id(component):
                return True
        return False

    
def is_having_resource(component,resource):
    with Resources._lock: 
        if Resources._using_resources[resource] == id(component) :
            return True
    return False


def stop_asking_for_resource(component,resource):
    with Resources._lock:
        try : Resources._asked_for_resource[resource].remove(id(component)) 
        except : pass
        try :
            if Resources._must_have_resource[resource]==id(component):
                Resources._must_have_resource[resource]=None
        except : pass

        
def release_resource(component,resource):
    with Resources._lock:
        try :
            using = Resources._using_resources[resource]
        except :
            Resources._using_resources[resource]=None
            using = None
        if using==id(component) :
            Resources._using_resources[resource]=None

            
def resources_used(component):
    with Resources._lock:
        return [ r for r in Resources._resources
                 if Resources._using_resources[r]==id(component) ]


class Resources_manager(object):


    def __init__(self,**kwargs):

        self._asked_resources = set()
        self._just_had_resources = set()
        self._had_resources = set() 
        self._denied_resources = set()
        self._has_resources = set() # updated by fResource
        self._commit_duration = None

        
    def reset(self):

        self.stop_asking_for_any_resource()
        self.release_all_resources()

        
    def ask_for_resource(self,resource):

        self._asked_resources.add(resource)
        r = ask_for_resource(self, resource)

        if r:
            self._just_had_resources.add(resource)
            self._denied_resources.discard(resource)
        else : self._denied_resources.add(resource)

        return r

    
    def take_resource(self,resource):
        
        self._asked_resources.add(resource)
        r = take_resource(self, resource)

        if r:
            self._just_had_resources.add(resource)
            self._denied_resources.discard(resource)

        else : self._denied_resources.add(resource)
        if r : self.commit()

        return r

    
    def is_having_resource(self,resource):
        
        return is_having_resource(id(self),resource)

    
    def used_resources(self):

        return [r for r in Resources.get_resources() if self.is_having_resource(r)]

    
    def had_resources(self,*resources):

        if not self._had_resources : return False

        if not resources : return True

        for r in resources :
            if r not in self._had_resources : return False

        return True

    
    def just_had_resources(self,*resources):

        if not self._just_had_resources: return False
        
        if resources is None or len(resources)==0:
            self._just_had_resources = set()
            return True
       
        if all([r in self._just_had_resources for r in resources]):
           self._just_had_resources = set()
           return True
       
        return False


    def take_resources(self,*resources):

        requests = [self.take_resource(r) for r in resources]
        r = all(requests)
        if r : self._just_had_resources.update(resources)
        return r

    
    def ask_for_resources(self,*resources):

        time_start = time.time()
        requests = [self.ask_for_resource(r) for r in resources]

        while not all(requests):
            if time.time()-time_start > 0.2 : break
            requests = [self.ask_for_resource(r) for r in resources]
            time.sleep(0.05)
            
        r = all(requests)
        if r : self._just_had_resources.update(resources)

        return r


    def stop_asking_for_resource(self,resource):

        try:self._asked_resources.remove(resource)
        except:pass
        self._denied_resources.discard(resource)
        stop_asking_for_resource(self,resource)

        
    def stop_asking_for_any_resource(self):

        resources_to_stop = [r for r in self._asked_resources]
        for r in resources_to_stop: self.stop_asking_for_resource(r)
        self._asked_resources = set()

        
    def finalize_resource(self,resource):

        self.stop_asking_for_resource(resource)
        self.release_resource(resource)

        
    def release_resource(self,resource):

        self._denied_resources.discard(resource)
        release_resource(self, resource)
        self._just_had_resources.discard(resource)
        self._had_resources.discard(resource)

        
    def release_all_resources(self):

        used = resources_used(self)
        self._just_had_resources = set()
        self._had_resources = set()
        for resource in used : self.release_resource(resource)
