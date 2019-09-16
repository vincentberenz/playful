# Copyright 2019 Max Planck Gesellschaft
# Author: Vincent Berenz

from ..resources.resources import Resources
from ..component.component import Component
from ..memory.memory import Memory
from ..display.display import Display


_GLOBALS = {}


def get_globals():
    return {k:v for k,v in _GLOBALS.items()}

def get_global(key) :
    return _GLOBALS[key]

def has_globals(key) :
    return key in list(_GLOBALS.keys())

def get_resource(resource) :
    return Resources._resources[resource]

def set_global(key,value) :
    _GLOBALS[key]=value




def registered_resources():
    
    with resources.Resources._lock:
        return [r for r in resources.Resources._resources]

    
def register_resources(*resources):
    
    if not all (isinstance(r,str) for r in resources) :
        raise Exception(str(resources))
    
    with resources.Resources._lock :
        for r in resources:
            r = r.replace("\n","")
            r = r.strip()
            if r not in resources.Resources._resources :
                resources.Resources._resources.append(r)
                resources.Resources._should_have_resource[r]=None
                resources.Resources._using_resources[r]=None
                resources.Resources._asked_for_resource[r]=[]
                resources.Resources._must_have_resource[r]=None


Node = Component
Memory = Memory

console = Display.console
unconsole = Display.unconsole
