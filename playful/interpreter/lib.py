# Copyright 2019 Max Planck Gesellschaft
# Author: Vincent Berenz


class Lib:
    
    tries = {}
    
    @classmethod
    def add_trie(cls,trie_name,trie):
        cls.tries[trie_name]=trie
        
    @classmethod
    def set_tries(cls,tries):
        cls.tries = tries

        
def set_libraries(lib_tries):
    Lib.set_tries(lib_tries)    
