# Copyright 2019 Max Planck Gesellschaft
# Author: Vincent Berenz


from .args import get_args_dict
from .lib import Lib
from ..memory.memory import Memory

class Preprocessed_word:
    
    fixed_value = 0
    scheme = 1
    property = 2
    extension = 3
    token_method = 4
    token_class = 5
    memory_key = 6

    
    def __init__( self,
                  original=None,
                  fixed_value=None,
                  scheme_id=None,
                  scheme_type=None,
                  name=None,
                  pointer= None,
                  related_property=None,
                  word_type=None,
                  lock=None,
                  args_dict={} ):

        locs = locals()
        for l in locs :
            setattr(self,l,locs[l])
        #self._scheme_id_and_type_same = False
        #if scheme_id is not None and scheme_type is not None:
        #    self._scheme_id_and_type_same = (scheme_type==Memory.get_scheme_type(scheme_id))

            
    def describe(self):
        
        s = dict( orginal=self.original,
                  fixed=self.fixed_value,
                  scheme_id=self.scheme_id,
                  scheme_type=self.scheme_type,
                  name=self.name,
                  pointer=self.pointer,
                  related_property=self.related_property,
                  word_type=self.word_type,
                  args=self.args_dict )
        s = {k:str(s[k]) for k in s}
        return s

    
    def evaluate(self):

        if self.scheme_id is not None:
            if self.scheme_type is not None:
                if "target" in self.args_dict.keys():
                    target = Memory.get(self.scheme_type,
                                        self.scheme_id)
                    self.args_dict["target"]=target
        
        def update_str(s): 
            if isinstance(s,str):
                return "'"+s+"'"
            return s
        
        if self.word_type == Preprocessed_word.memory_key:
            try :
                return update_str(Memory.copy(self.name))
            except :
                return None
            
        if self.word_type == Preprocessed_word.fixed_value :
            return update_str(self.fixed_value)
        
        if self.word_type == Preprocessed_word.scheme:
            return Memory.get_number_of_schemes(self.scheme_type)
        
        if self.word_type == Preprocessed_word.property: 
            if self.pointer is None :
                try :
                    if self.scheme_id :
                        self.pointer,self.lock = Memory.get(self.scheme_id,self.name)
                    elif self.scheme_type :
                        self.pointer,self.lock = Memory.get(self.scheme_type,self.name)
                    else :
                        self.pointer,self.lock = Memory.get(self.name)
                except :
                    return None
                with self.lock :
                    return bool(self.pointer)
                
        if self.word_type == Preprocessed_word.extension : 
            if self.scheme_id is not None and self.scheme_type is not None and not self._scheme_id_and_type_same : 
                for p in self.related_property:
                    r = Memory.get_property_extension_value(self.scheme_type,self.name,p)
                    if r and len(r)>0 and not r[0] is None: return r[0]
                return update_str(r)
            if self.scheme_id is not None :
                for p in self.related_property:
                    r = Memory.get_property_extension_value(self.scheme_id,
                                                            self.name,
                                                            related_property=p,
                                                            **self.args_dict)
                    if r is not None :
                        return update_str(r)
                return r
            else :
                for p in self.related_property:
                    r = Memory.get_property_extension_value(self.scheme_type,self.name,p)
                    if r and len(r)>0 and not r[0] is None:
                        return update_str(r)
                return update_str(r)
            
        if self.word_type == Preprocessed_word.token_method :
            r = self.pointer(**self.args_dict)
            return r

        if self.word_type == Preprocessed_word.token_class :
            instance = self.pointer(**self.args_dict)
            try :return float(instance)
            except:
                try : return int(instance)
                except : return bool(instance)
        return None

    
    @classmethod
    def preprocess( cls,
                    word,
                    scheme_id=None,
                    scheme_type=None,
                    **kwargs):
        
        word = word.strip()
        
        if word in Lib.tries["scheme"]:
            return Preprocessed_word( original=word,
                                      scheme_id=scheme_id,
                                      scheme_type=word,
                                      word_type=Preprocessed_word.scheme)
        
        if word in Lib.tries["property"] :
            return Preprocessed_word( original=word,
                                      scheme_id=scheme_id,
                                      word_type=Preprocessed_word.property,
                                      name=word)
        
        if word in Lib.tries["extension"] :
            w = Lib.tries["extension"][word]
            required_args = copy.deepcopy(w.kwargs)
            for arg,val in [k for k in kwargs if k in required_args] :
                required_args[arg]=val
            return Preprocessed_word( original=word,
                                      scheme_id=scheme_id,
                                      scheme_type=scheme_type,
                                      word_type=Preprocessed_word.extension,
                                      related_property=w.related_properties,
                                      name=word,
                                      args_dict=required_args)
        
        
        if word in Lib.tries["token"] :
            w = Lib.tries["token"][word]
            callable_ = w.class_
            is_component, args = get_args_dict(callable_,**kwargs)
            if "scheme_id" in args :
                args["scheme_id"]=scheme_id
            if "scheme_type" in args :
                args["scheme_type"]=scheme_type
            if is_component :
                return Preprocessed_word( original=word,
                                          scheme_id=scheme_id,
                                          scheme_type=scheme_type,
                                          word_type=Preprocessed_word.token_class,
                                          name=word,
                                          pointer=callable_,
                                          args_dict=args )

            else :
                return Preprocessed_word(original=word,
                                         scheme_id=scheme_id,
                                         scheme_type=scheme_type,
                                         word_type=Preprocessed_word.token_method,
                                         name=word,pointer=callable_,
                                         args_dict=args)
            
        if word in Lib.tries["memory_key"]:
            return Preprocessed_word(original=word,
                                     word_type=Preprocessed_word.memory_key,
                                     name=word)
        
        dot_index = None;
        
        try :
            dot_index = word.index(".")
        except :
            pass
        
        if dot_index is not None:
            try : 
                try : float_value = float(word)
                except:
                    float_value = float(eval(word,{},{}))
                Preprocessed_word(original=word,
                                  word_type=Preprocessed_word.fixed_value,
                                  fixed_value=float_value)
            except:
                scheme_type = word[:dot_index]
                property_or_extension = word[dot_index+1:]
                if scheme_type not in Lib.tries["scheme"]:
                    raise Exception("Could not evaluate "+
                                    word+" : "+
                                    scheme_type+" is not a registered scheme type")
                if property_or_extension in Lib.tries["property"] :
                    return Preprocessed_word(original=word,
                                             word_type=Preprocessed_word.property,
                                             scheme_id=scheme_id,
                                             scheme_type=scheme_type,
                                             name=word)
                elif property_or_extension in Lib.tries["extension"] :
                    return Preprocessed_word(original=word,
                                             word_type=Preprocessed_word.extension,
                                             scheme_id=scheme_id,
                                             scheme_type=scheme_type,
                                             name=property_or_extension,
                                             related_property = Lib.tries["extension"][word].related_properties)
                else :
                    raise Exception("Could not evaluate "+word
                                    +" : "+property_or_extension
                                    +" is not a registered property or property extension")
        # boolean replaced by themselves
        if word.lower()=="true":
            return Preprocessed_word(original=word,
                                     word_type=Preprocessed_word.fixed_value,
                                     fixed_value=True)
        if word.lower()=="false":
            return Preprocessed_word(original=word,
                                     word_type=Preprocessed_word.fixed_value,
                                     fixed_value=False)
        # numbers replaced by themselves
        try:
            return Preprocessed_word(original=word,
                                     word_type=Preprocessed_word.fixed_value,
                                     fixed_value=float(word))
        except :
            pass
        try: return Preprocessed_word(original=word,
                                      word_type=Preprocessed_word.fixed_value,
                                      fixed_value=int(word))
        except :
            pass
        return None
