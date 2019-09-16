# Copyright 2019 Max Planck Gesellschaft
# Author: Vincent Berenz


import math
from .preprocessed_word import Preprocessed_word

def _return_none() :
    return None

def _sup_or_eq(a,b):
    return cmp(a,b)>=0

def _sup(a,b):
    return cmp(a,b)>0

def _inf_or_eq(a,b):
    return cmp(a,b)<=0

def _inf(a,b):
    return cmp(a,b)<0

def _eq(a,b):
    return cmp(a,b)==0



class Subevaluation:
    
    _valid_operators = ('<','>','>=', '<=','=','==')
    _replace_operators = {'is':'=', '==':'=' , 'different':'!=', 'same':'=', 'exists':'exist'}
    _operator_dict = {'>':_sup,'<':_inf,'>=':_sup_or_eq,'<=':_inf_or_eq,'=':_eq,'exist':_return_none}
    _any = 1
    _all = 2
    
    def __init__( self,
                  sub_evaluation,scheme_id=None,
                  scheme_type=None,
                  **kwargs ):
        
        self._original = sub_evaluation
        self._preprocessed_eval = []
        self._negate = False
        self._operator = None
        self._operator_index = None
        self._left_any_all = None
        self._right_any_all = None
        self._any_or_all = False
        self._has_any = False
        self._has_all = False
        sub_evaluation.strip()
        
        for r in Subevaluation._replace_operators :
            sub_evaluation.replace(r,Subevaluation._replace_operators[r])
            
        words = sub_evaluation.split()
        
        for w in words :
            if w.lower() == "not" :
                self._negate = True
            else : 
                preprocessed = Preprocessed_word.preprocess(w, scheme_id, scheme_type,**kwargs)
                if preprocessed is None :
                    self._preprocessed_eval.append(w)
                else :
                    self._preprocessed_eval.append(preprocessed)
                    
        for op in Subevaluation._valid_operators: 
            try:
                self._operator_index = self._preprocessed_eval.index(op)
                self._operator = Subevaluation._operator_dict[op]
                break
            except:
                pass
            
        if "any" in self._preprocessed_eval :
            self._has_any = True
            
        if "all" in self._preprocessed_eval :
            self._has_all = True
            
        if "any" in self._preprocessed_eval or "all" in self._preprocessed_eval :
            self._any_or_all = True
            
        if self._operator_index is not None :
            
            if "any" in self._preprocessed_eval[:self._operator_index] :
                self._left_any_all = self._any
                
            elif "all" in self._preprocessed_eval[:self._operator_index] :
                self._left_any_all = self._all
                
            if "any" in self._preprocessed_eval[self._operator_index:] :
                self._right_any_all = self._any
                
            elif "all" in self._preprocessed_eval[self._operator_index:] :
                self._right_any_all = self._all
                
        if self._left_any_all is None :
            self._left_any_all = self._any
            
        if self._right_any_all is None :
            self._right_any_all = self._any

        self.__nonzero__ = self.__bool__
            
    def original(self):
        return self._original
    
    def _evaluate_any_or_all_expression(self,transformed_eval):
        
        if self._operator_index is None :
            if len(transformed_eval)>2 :
                raise Exception("Failed to evaluate : "+str(self._original)
                                +" : correspond to the transformed evaluation : "
                                +str(transformed_eval)+" : not supported")
            if transformed_eval[1] is None :
                return False
            if not (isinstance(transformed_eval[1],list) and not isinstance(transformed_eval[1],str)):
                raise Exception("Failed to evaluate : "
                                +str(self._original)
                                +" : correspond to the transformed evaluation : "
                                +str(transformed_eval)+" : not supported")
            if len(transformed_eval[1])==0:
                return False
            if self._has_all :
                return eval("all ("+str(transformed_eval[1])+")",{},{})
            if self._has_any :
                return eval("any ("+str(transformed_eval[1])+")",{},{})
            raise Exception("Can not evaluate expression "
                            +self._original+" : operator missing")
        try :
            left_val = [e for e in transformed_eval[:self._operator_index] if e !="any" and e!="all"][0]
            right_val = [e for e in transformed_eval[self._operator_index+1:] if e !="any" and e!="any"][0]
            if left_val == [] or right_val==[] :
                return False
            if not isinstance(left_val,collections.Iterable) :
                left_val = [left_val]
            if not isinstance(right_val,collections.Iterable) :
                right_val = [right_val]
        except :
            raise Exception("Could not evaluate "+
                            self._original+
                            " : value to be compared missing")
        
        if self._left_any_all==self._any:
            all_evals = [cmp(l,r) for l in left_val for r in right_val]
            all_evals = [self._operator(c,0) for c in all_evals]
            if self._right_any_all==self._any: return any(all_evals)
            else :return all(all_evals)
            
        if self._left_any_all==self._all and self._right_any_all==self._any: 
            for l in left_val :
                all_evals = [cmp(l,r) for r in right_val]
                all_evals = [self.operator(c) for c in all_evals]
                if not any(all_evals) : return False
            return True
        
        if self._left_any_all==self._all and self._right_any_all==self._all: 
            for l in left_val :
                all_evals = [cmp(l,r) for r in right_val]
                all_evals = [self.operator(c) for c in all_evals]
                if not all(all_evals) : return False
            return True
        
        raise Exception("failed to evaluated : "+str(self._orginal))
    
    @staticmethod
    def _smart_str(e):
        if str(e)=="inf": return "float('+inf')"
        if str(e)=="-inf": return "float('-inf')"
        return str(e)
    
    def __bool__(self):

        transformed_evaluation = [e if isinstance(e,str) else e.evaluate()
                                  for e in self._preprocessed_eval]
        
        if self._any_or_all :
            r = self._evaluate_any_or_all_expression(transformed_evaluation)
            
        else :
            to_eval = "".join([self._smart_str(e) for e in transformed_evaluation])
            try : 
                r = eval(to_eval,{"pi":math.pi},{"pi":math.pi})
            except Exception as e: 
                return False
            
        if not isinstance(r,bool):
            raise Exception(" | evaluation : ["+self._original+"] evaluated as : "+str(r)+" (not a boolean)")
        
        if self._negate : return (not
                                  r)
        return r
