# Copyright 2019 Max Planck Gesellschaft
# Author: Vincent Berenz


import os,traceback,imp,inspect,collections
from .interpreter import playful_to_python
from .workspace import Workspace
from .word import Word
from ..engine.run import run as run_playful
from .lib import set_libraries
from ..api.api import has_globals
from ..component.component import Component
from ..api.api import set_global,get_global

class Member:

    __slots__ = [ "name","obj",
                  "is_function",
                  "is_built_in",
                  "is_class",
                  "file_name",
                  "code","line_number",
                  "args" ]
    
    def __init__( self,
                  name,
                  obj,
                  is_function,
                  is_built_in,
                  is_class,
                  file_name,
                  code,
                  line_number,args ):

        locs = locals()
        for slot in self.__slots__:
            setattr(self,slot,locs[slot])

    def __str__(self):

        return "\n".join( [ slot+": "+str(getattr(self,slot))
                            for slot in self.__slots__ ] )


def get_obj_kwargs(obj):
    
    argspec = inspect.getargspec(obj)
    if argspec.defaults is None :
        return {}
    args = [a for a in argspec.args if a!="self"]
    return {a:v for a,v in zip(args,argspec.defaults)}

    
def get_globals_vocabulary(global_file_or_module_or_dict):
    
    if isinstance(global_file_or_module_or_dict,str):
        module_ = imp.load_source(os.path.basename( global_file_or_module_or_dict[:-3]),
                                  global_file_or_module_or_dict )
        
    elif not isinstance(global_file_or_module_or_dict,dict) :
        module_ = iter(global_file_or_module_or_dict.items())
        
    if isinstance(global_file_or_module_or_dict,dict) :
        members = iter(global_file_or_module_or_dict.items())
        
    else :
        members = inspect.getmembers(module_)
    
    r = []
    for name,obj in members:
        if not name.startswith('_'):
            is_function = inspect.isfunction(obj)
            is_class = inspect.isclass(obj)
            is_built_in = inspect.isbuiltin(obj)
            try : file_name = inspect.getfile(obj)
            except : file_name = None
            try : code,line_number = inspect.getsourcelines(obj)
            except : code,line_number = None,None
            try :
                argspec = inspect.getargspec(obj)
                if argspec.defaults is not None :
                    args = [a for a in argspec.args if a!="self"]
                    args =  {a:v for a,v in zip(args,argspec.defaults)}
                else : args = {}
            except : args = None
            r.append(Member( name,
                             obj,
                             is_function,
                             is_built_in,
                             is_class,
                             file_name,code,
                             line_number,
                             args ) )
    return r


# important note : just by creating an instance of vocabulary, all folders of all working spaces are added to python path and __init__.py are added all over the place
# important note : also make global all the variables defined in various globals.py files
class Vocabulary():
    
    grammar = [ "while",
                "none",
                "not",
                "priority of",
                "targeting",
                "exist",
                "is",
                "different",
                "and",
                "or",
                "scheme" ]

    __slots__ = ["trail_only","warnings",
                 "_tries","_trail","_vocabulary"]

    
    def __init__(self,folder_path,trail_only=False):
        
        self.trail_only = trail_only
        self.warnings = []
        self._tries = {t:{} for t in Word.types}
        for w in self.grammar :
            self._tries["grammar"][w]= Word(w,'grammar',None,None,None,None)
        self._trail = Workspace(folder_path).get_execution_trail()
        self._vocabulary = []
        self._building_vocabulary(folder_path)

        
    def _building_vocabulary(self,folder_path):

        if not self.trail_only:
            for file_path in self._trail.globals_ + self._trail.py + self._trail.rt :
                try:
                    self._vocabulary.extend(self._get_file_vocabulary(file_path))
                except Exception as e:
                    traceback.print_exc()
                    error = "failed to read file "+str(file_path)+" with error: "+str(e) 
                    raise Exception(error)
        else :
            for file_path in self._trail.py + self._trail.rt :
                try:
                    self._vocabulary.extend(self._get_file_vocabulary(file_path))
                except Exception as e:
                    traceback.print_exc()
                    error = "failed to read file "+str(file_path)+" with error: "+str(e) 
                    raise Exception(error)
                
        resources = []
        
        for resource_file in self._trail.resources:
            
            def _read_resources(path):
                with open(path,"r") as f : lines = f.readlines()
                for line in lines : 
                    l = line.strip()
                    if not l.startswith("#"): resources.append(l)
            _read_resources(resource_file)

        # deprecated: resources are no longer declared in file, but created on the
        #             fly by components
        #register_resources(*resources)
        
        for w in self._vocabulary: 
            if w.type is None or w.type not in Word.types :
                raise Exception("word of unknown type:"+str(w))
            if w.name not in self._tries[w.type] :
                self._tries[w.type][w.name]=w
            else :
                try :
                    self._tries[w.type][w.name].related_properties.extend(w.related_properties)
                except : pass
                
    def get_execution_trail(self):
        return self._trail.py + self._trail.rt + self._trail.globals_ + self._trail.resources + self._trail.on_start + self._trail.on_stop
    
    def get_components(self):
        return list(self._tries["component"].keys())
    
    def get_schemes(self):
        return list(self._tries["scheme"].keys())
    
    def get_conditionals(self):
        r = []
        types = ["scheme","property","extension","token","memory_key"]
        for t in types :
            r.extend(list(self._tries[t].keys()))
        return r
    
    def is_valid_component(self,component_name):
        return component_name in list(self._tries["component"].keys())
    
    def is_valid_conditional_word(self,word_):
        types = ["scheme","property","extension","token","memory_key"]
        return any( [word_ in list(self._tries[t].keys()) for t in types] )
    
    def get_warnings(self):
        if not self.warnings : return None
        return self.warnings
    
    def get_workspace(self):
        return self._ws
    
    def get_trail(self):
        return self._trail
    
    def get_word(self,word_name,*types):
        if types : Word.check_types(*types)
        if not types : types=Word.types
        for type_ in types:
            try : return self._tries[type_][word_name]
            except : pass
        return None
    
    def get_words_of_file(self,file_name,*types):
        if types : Word.check_type(*types)
        if not types : types=Word.types
        if len(types)==1:
            return [w for w in list(self._tries.values()) if w.origin==file_name]
        else:
            r = []
            for type_ in types: r.extend(self.get_words_of_file(file_name,type_))
            return r

        
    def execute(self,overwrite_globals=None,
                exit_on_q=True):
        
        self.raise_exception()
        set_libraries(self._tries)
        
        if overwrite_globals:
            for g,v  in overwrite_globals.items(): set_global(g,v)
            
        for on_start in self._trail.on_start:
            print("executing:\t",on_start)
            imp.load_source(os.path.basename(on_start[:-3]),on_start)
            
        should_set_report_in_memory = False
        should_print_report = False
        should_generate_tree_representation = False
        
        try :
            should_print_report = get_global("PRINT_REPORT")
        except : pass
        
        try :
            should_set_report_in_memory = get_global("SHARE_REPORT")
        except : pass
        try :
            should_generate_tree_representation = get_global("TREE_REPRESENTATION")
        except : pass
        
        run_playful( print_report=should_print_report,
                     share_report=should_set_report_in_memory,
                     tree_representation=should_generate_tree_representation,
                     exit_on_q=exit_on_q)
        
        for on_stop in self._trail.on_stop:
            print("executing:\t",on_stop)
            imp.load_source(os.path.basename(on_stop[:-3]),on_stop)

            
    def get_vocabulary(self,*types):
        if not types: types = Word.types
        else : Word.check_type(*types)
        t = {}
        for type_ in types : 
            for k,v in self._tries[type_].items() : t[k]=v
        return t

    
    def autocomplete(self,prefix,*types):
        if not types : types = Word.types
        else : Word.check_type(*types)
        prefixes = []
        for type_ in types :
            prefixes.extend(self._tries[type_].items(prefix=prefix))
        prefixes = [p for p in prefixes if p]
        return [p[1] for p in prefixes]

    
    def autocomplete_dotted_scheme(self,prefix,related_scheme):
        r = self.autocomplete(prefix,"property","extension")
        return [p for p in r if related_scheme in p.related_schemes]

    
    def program_issues(self):
        if not "program" in self._tries["fractal"] :
            return "failing to find entry point ('program' node in any .play file)"
        return None

    
    def name_mangling(self):
        names  = [w.name
                  for w in self._vocabulary
                  if w.type is not None and w.type != "extension" and w.type != "memory_key"]
        counts = collections.Counter(names)
        duplicates = [n for n in names if counts[n]>1]
        r = {}
        for d in duplicates:
            words = [w for w in self._vocabulary if w.name==d]
            r[d]=words
        return r

    
    def raise_exception(self):
        def print_word(word):
            return word.name+" "+str(word.origin)
        issues = []
        manglings = self.name_mangling()
        for mangling,words in manglings.items():
            issues.append("name mangling detected:"+
                          mangling+"\n\t"+
                          "\n\t".join([print_word(w) for w in words]))
        prog_issues = self.program_issues()
        if prog_issues is not None :
            issues.append(prog_issues)
        if issues :
            raise Exception("\n".join(issues))

        
    def get_word(self,name,*types):
        if types : Word.check_type(*types)
        else : types = Word.types
        for type_ in types:
            if name in self._tries[type_] : return self._tries[type_][name]
        return None

    
    def _get_globals_vocabulary(self,global_file): 
        vocabulary = []
        members = get_globals_vocabulary(global_file)
        for member in members :
            if not member.name.startswith("_"):
                set_global(member.name,member.obj)
        return vocabulary

    
    def _get_python_vocabulary(self,py_file_or_module_or_dict):

        def should_add_to_vocabulary(member):
            try :
                if member.name.startswith("_") :
                    return False # no, private
                if has_globals(member.name) :
                    return False # no, global, already added from another globals.py file
                if member.is_built_in :
                    return False # no, build in
                if not isinstance(py_file_or_module_or_dict,
                                  dict) and not ( member.file_name == py_file_or_module_or_dict or member.file_name==(py_file_or_module_or_dict+"c") ) :
                    return False # no, import (not declared in this file)
                return True
            except :
                return False # probably some builtin stuff that has things above fail
            
        def get_item(member,type_,kwargs={},name=None):
            code,line_number = member.code,member.line_number
            if name is None : 
                if member.name is None : name = member.obj.__name__
                else : name = member.name
            return Word(name,
                        type_,
                        py_file_or_module_or_dict,
                        line_number,code,member.obj,
                        kwargs=kwargs)
        
        members = get_globals_vocabulary(py_file_or_module_or_dict)
        vocabulary = []
        
        for member in members :

            if should_add_to_vocabulary(member):

                if member.is_function:
                    vocabulary.append(get_item(member,"token",kwargs=get_obj_kwargs(member.obj)))
                    
                if member.is_class:
                    
                    if issubclass(member.obj,Component):
                        obj_kwargs = get_obj_kwargs(member.obj.__init__) 
                        vocabulary.append(get_item(member,"component",obj_kwargs))
                        try :
                            memory_keys = member.obj.memory_keys()
                            if isinstance(memory_keys,str): memory_keys=[memory_keys]
                            for mk in memory_keys:
                                vocabulary.append(get_item(member,"memory_key",name=mk))
                        except : pass
                        
                    else : vocabulary.append(get_item(member,"token"))
                    
        return vocabulary
    
    def _get_file_vocabulary(self,rt_or_py_file):

        if os.path.basename(rt_or_py_file).startswith(".") :
            return []
        
        if rt_or_py_file.endswith("globals.py") :
            return self._get_globals_vocabulary(rt_or_py_file)
        
        if rt_or_py_file.endswith("_play.py") :
            return self._get_python_vocabulary(rt_or_py_file)
        
        if rt_or_py_file.endswith(".play") :
            return playful_to_python(rt_or_py_file)
        
        return []
