# Copyright 2019 Max Planck Gesellschaft
# Author: Vincent Berenz


from .args import get_args_dict
from .lib import Lib
from ..memory.memory import Memory

# calculator might be a fixed value (including none), a token method or a token class

class Preprocessed_calculator (object) :

    fixed_value = 0
    token_method = 1
    token_class = 2
    property = 3
    extension = 4
    memory_key = 5
    
    def __init__( self,
                  original=None,
                  ini_calculator=None,
                  fixed=None,
                  scheme_id=None,
                  scheme_type=None,
                  name=None,
                  pointer=None,
                  word_type=None,
                  related_property=None,
                  lock=None,
                  args_dict={} ):
        
        locs = locals()
        for l in locs :
            setattr(self,l,locs[l])
        
    def __str__(self):
        r = str( "preprocessed calculator : "
                 +self.original
                 +" evaluated at "+str(float(self)))
        return r
                    
    def __float__(self): 
        r = self.evaluate()
        return float(r)
                    
    def evaluate(self):
      
        if self.scheme_id is not None:
            if self.scheme_type is not None:
                if "target" in self.args_dict.keys():
                    target = Memory.get(self.scheme_type,
                                        self.scheme_id)
                    self.args_dict["target"]=target
        
        def update_str(s) :
            if isinstance(s,str):
                return "'"+s+"'"
            return s
                    
        if self.word_type == Preprocessed_calculator.fixed_value :
            return update_str(self.fixed)
                    
        if self.word_type == Preprocessed_calculator.memory_key : 
            try :
                return update_str(Memory.copy(self.name))
            except :
                return float("-inf")
                    
        if self.word_type == Preprocessed_calculator.token_method : 
            try :
                return update_str(self.pointer(**self.args_dict))
            except :
                return update_str(self.pointer.__call__(**self.args_dict))
            
        if self.word_type == Preprocessed_calculator.token_class :

            instance = self.pointer(**self.args_dict)
            try :
                return float(instance)
            except:
                try :
                    return int(instance)
                except :
                    raise Exception("failed to evaluate a preprocessed calculator "+str(self.ini_calculator))
                
        if self.word_type == Preprocessed_calculator.property:
            if self.pointer is None:
                try:
                    if self.scheme_id :
                        self.pointer,self.lock = Memory.get_property(self.name,self.scheme_id)
                    elif self.scheme_type :
                        self.pointer,self.lock = Memory.get_property(self.name,self.scheme_type)
                    else :
                        self.pointer,self.lock = Memory.get_property(self.name)
                except :
                    return float("-inf")
            with self.lock : return float(self.pointer)
            
        if self.word_type == Preprocessed_calculator.extension :
            for p in self.related_property:
                r = Memory.get_property_extension_value(self.scheme_id, self.name,related_property=p,**self.args_dict)
                if r is None: return -1
                if r is not None : return update_str(r)
            return update_str(r)
        
        return None

    
    @classmethod
    def preprocess( cls,
                    word,
                    scheme_id=None,
                    scheme_type=None,
                    **kwargs ) :

        word = word.strip()
        
        if word in Lib.tries["token"] :
            callable_ = Lib.tries["token"][word].class_
            is_component, args = get_args_dict(callable_,**kwargs)
            if "scheme_id" in args :
                args["scheme_id"]=scheme_id
            if is_component :
                return Preprocessed_calculator(word,
                                               scheme_id=scheme_id,
                                               scheme_type=scheme_type,
                                               ini_calculator=word,
                                               word_type=Preprocessed_calculator.token_method,
                                               name=word,
                                               pointer=callable_,
                                               args_dict=args)
            else :
                return Preprocessed_calculator(word,
                                               scheme_id=scheme_id,
                                               scheme_type=scheme_type,
                                               ini_calculator=word,
                                               word_type=Preprocessed_calculator.token_class,
                                               name=word,pointer=callable_,
                                               args_dict=args)
            
        if word in Lib.tries["property"] :
            return Preprocessed_calculator(original=word,
                                           ini_calculator=word,
                                           scheme_id=scheme_id,
                                           word_type=Preprocessed_calculator.property,
                                           name=word)
        
        if word in Lib.tries["extension"] :
            w = Lib.tries["extension"][word]
            required_args = copy.deepcopy(w.kwargs)
            for arg,val in { k:v
                             for k,v in kwargs.items()
                             if k in required_args }.items() :
                required_args[arg]=val
            return Preprocessed_calculator(original=word,
                                            ini_calculator=word,
                                            word_type=Preprocessed_calculator.extension,
                                            related_property = w.related_properties,
                                            name=word,
                                            args_dict=required_args,
                                            scheme_id=scheme_id,
                                            scheme_type=scheme_type)
        if word in Lib.tries["memory_key"]:
            return Preprocessed_calculator(original=word,
                                            ini_calculator=word,
                                            word_type=Preprocessed_calculator.memory_key,
                                            name=word)
        
        return Preprocessed_calculator(word,
                                       scheme_id=scheme_id,
                                       scheme_type=scheme_type,
                                       ini_calculator=word,
                                       word_type=Preprocessed_calculator.fixed_value,
                                       fixed=float(word))
