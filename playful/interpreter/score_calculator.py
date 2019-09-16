# Copyright 2019 Max Planck Gesellschaft
# Author: Vincent Berenz



from .evaluation import Evaluation
from .preprocessed_calculator import Preprocessed_calculator
from .preprocessed_word import Preprocessed_word


class Score_calculator:
    
    def __init__(self,
                 evaluation,
                 calculator,
                 original):

        self._evaluation, self._calculator, self._original = evaluation,calculator,original
        self.__nonzero__ = self.__bool__
        
    def __str__(self):
        return self._original
    
    def __bool__(self):
        if self._calculator is None :
            return False
        b = bool(self._evaluation)
        return b
        
    def __float__(self):
        return float(self._calculator)


class Score_calculator_str:
    
    def __init__(self,
                 evaluation_str,
                 calculator_str,
                 **kwargs):
        self._evaluation_str, self._calculator_str, self._kwargs = evaluation_str,calculator_str,kwargs
        
    def get_score_calculator(self,scheme_id,scheme_type):
        try :
            evaluation = Evaluation.read( self._evaluation_str,
                                          scheme_id,
                                          scheme_type,
                                          **self._kwargs )
        except Exception as e :
            raise Exception("\nplayful interpreter error: failed to preprocess the evaluation : "+
                            str(self._evaluation_str)
                            +" : "+str(e)+"\n")
        try :
            calculator = Preprocessed_calculator.preprocess(self._calculator_str,
                                                            scheme_id,
                                                            scheme_type,
                                                            **self._kwargs)
        except Exception as e :
            raise Exception("\nplayful interpreter error: failed to preprocess score calculator : "+
                            str(self._calculator_str)+" : "+str(e)+"\n")
        
        return Score_calculator(evaluation,
                                calculator,
                                "evaluation: "+
                                self._evaluation_str+
                                ", calculator : "+
                                self._calculator_str)
    
    def __str__(self):
        return str(self._evaluation_str)+" "+str(self._calculator_str)
    
    @classmethod
    def clean(cls,s):
        return s.replace("otherwise"," ")
    
    @classmethod
    def read(cls,s,**kwargs):
        s = Score_calculator_str.clean(s).strip()
        if 'if' not in s :
            return Score_calculator_str("True",
                                        s.strip(),
                                        **kwargs)
        return Score_calculator_str(s[s.index('if')+2:].strip(),
                                    s[:s.index('if')].strip(),
                                    **kwargs)

