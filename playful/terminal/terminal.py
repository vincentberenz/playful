# Copyright 2019 Max Planck Gesellschaft
# Author: Vincent Berenz


import sys,os
from ..interpreter.vocabulary import Vocabulary
from ..engine.run import running


def current_dir():
    return os.getcwd()


def execute(path,config_globals=None):
    if path is None:
        v = Vocabulary(current_dir())
    else :
        v= Vocabulary(path)
    v.execute(config_globals,exit_on_q=False)

    
def stop():
    running.running = False
    
def get_vocabulary(root_folder,program_name) :
    return vocabulary(root_folder,program_name)


def add_current_dir_to_python_path():
    sys.path.insert(1,current_dir())


def print_trail():
    v = Vocabulary(current_dir(),trail_only=True)
    print()
    print("\n".join(v.get_execution_trail()))
    print()


def print_word(word_name):
    v = Vocabulary(current_dir(),trail_only=True)
    word = v.get_word(word_name)
    if word is not None : 
        print("type : "+str(word.type))
        print("orgin : "+str(word.origin))
        print("line : "+str(word.line))
        try:
            print("code : \n"+"".join(word.code))
        except :
            print("--- could not print code")
    else :
        print(str(word_name)+" not found")


def print_vocabulary(program_name):
    v = Vocabulary(current_dir(),program_name)
    words = list(v.get_vocabulary().values())
    for w in words: print(w)
