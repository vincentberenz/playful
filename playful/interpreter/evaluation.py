# Copyright 2019 Max Planck Gesellschaft
# Author: Vincent Berenz


import threading
from .subevaluation import Subevaluation        
  
class Evaluation:
    
    _lock = threading.Lock()
    
    def __init__( self,
                  a,
                  scheme_id,
                  scheme_type,
                  **kwargs ):

        self._original = a
        
        if isinstance(a,str) or len(a)==1:
            if not isinstance(a,str) : a = a[0]
            self.left = Subevaluation(a,scheme_id,scheme_type,**kwargs)
            self.right,self.operator = True,'and'
            self.next = None
            
        elif len(a)>=3 :
            self.left = Subevaluation(a[0],scheme_id,scheme_type,**kwargs)
            self.right = Subevaluation(a[2],scheme_id,scheme_type,**kwargs)
            self.operator = a[1]
            assert self.operator=='or' or self.operator=="and"
            self.next = None
            if len(a)>3:
                self.next_operator = a[3]
                assert self.next_operator=="or" or self.next_operator=="and"
                self.next =Evaluation(a[4:],scheme_id,scheme_type,**kwargs)

        else  :
            raise Exception(str(a))

        # for working in both python2 and 3
        self.__next__ = self.next
        self.__nonzero__ = self.__bool__
        
    @classmethod
    def read(cls,s,scheme_id,scheme_type,**kwargs):
        
        def parse(s,container=None):
            
            def treat_evaluation(s):
                to_broaden = (">","<","==","=",">=","<=","(",")")
                for tb in to_broaden : s = s.replace(tb," "+tb+" ")
                s = s.replace("> =",">=")
                s = s.replace("< =" ,"<=")
                s = s.replace("=  =","==")
                s = s.split()
                new_s = []
                current = ""
                kwords = ["(",")","or","and"]
                added = False
                for i in range(len(s)) :
                    if s[i] not in kwords :
                        added = False
                        current += s[i]+" "
                    else:
                        if current != '': new_s.append(current.strip())
                        new_s.append(s[i])
                        added = True
                        current = ""
                    if i==len(s)-1 and not added : new_s.append(current.strip())
                return new_s
            
            if container is None :
                return parse(treat_evaluation(s),container=[])
            
            my_array = []
            i = 0
            
            while i < len(s):
                if s[i]!="(" and s[i]!=")":
                    my_array.append(s[i])
                    i+=1 
                elif s[i]=="(" :
                    end_index = parse(s[i+1:],container=my_array)
                    i += end_index+1
                elif s[i]==")":
                    container.append(my_array)
                    return i+1
            return my_array
        
        def first_opened_last_closed(s):
            
            if s[0]=='(':
                if s[-1]!=')' : return False
                open_ = 1;
                close_ = 0;
                for i in range(1,len(s)-1):
                    if s[i]=='(' : open_ = open_+1
                    elif s[i]==')' : close_ = close_+1
                    if open_ == 0 : return False
                    
            return False
        
        def set_suitable_parenthesis(s):
            
            if not s.count('(')==s.count(')') :
                raise Exception('mismatched parenthesis : '+s)
            s = s.strip()
            while first_opened_last_closed(s) : s = s[1:-1]
            return s
        
        evaluation_str = parse(set_suitable_parenthesis(s))
        return Evaluation(evaluation_str,scheme_id,scheme_type,**kwargs)
    
    def __str__(self):
        s = []
        if isinstance(self.left,str) or isinstance(self.left,bool):
            s.append(str(self.left))
        else : s.append(" left expression ")
        if self.operator == "or" : s.append(" or ")
        else : s.append(" and ")
        if isinstance(self.right,str) or isinstance(self.right,bool) :
            s.append(str(self.right))
        else : s.append(" right expression ")
        if self.__next__ is not None :
            assert self.next_operator == "or" or self.next_operator == "and"
            if self.next_operator == "or" : s.append(" or next ")
            else : s.append(" and next ")
        return "".join(s)
    
    def size(self):
        count = 0
        if isinstance(self.left,str) or isinstance(self.left,bool) or isinstance(self.left,Subevaluation):
            count+=1
        else : count+=self.left.size()
        if isinstance(self.right,str) or isinstance(self.right,bool) or isinstance(self.right,Subevaluation) :
            count+=1
        else : count+=self.right.size()
        if self.__next__ is not None :
            count+=self.next.size()
        return count
    
    def _root_evaluation(self):

        if self.operator == 'or' :
            r = (bool(self.left) or bool(self.right))
        else :
            r = (bool(self.left) and bool(self.right))
        return r
    
    def _evaluation(self,previous=False,operator="or"):

        if operator=="and" and previous is False :
            return False
        
        current_eval = self._root_evaluation()
        
        if operator == "or" :
            total_eval = previous or current_eval
        else :
            total_eval = previous and current_eval
        
        if self.__next__ is None :
            return total_eval
        
        return self.next._evaluation(total_eval, self.next_operator)
    
    def __bool__(self):
        r = self._evaluation()
        return r
