# Copyright 2019 Max Planck Gesellschaft
# Author: Vincent Berenz


import os,sys
from .directory import Directory


class Workspace:


    __slots__ = ["rt_directories"]

    
    def __init__(self,path):
        
        self.rt_directories = []
        
        # we go up the tree as long as we find __playful__ files.
        # and consider the top directory as the workspace directory (root_dir)
        # note: create __init__.py files in main and py folders
        playful_dir = True
        root_dir = None
        current_dir = path
        
        while playful_dir:
            new_dir = os.path.abspath(current_dir+os.sep+"..")
            playful_dir = "__playful__" in [f for f in os.listdir(new_dir)]
            if playful_dir : current_dir=new_dir
            
        # adding top directory (possibly fractal/tree) to python path
        root_dir = os.path.abspath(new_dir)
        sys.path.append(root_dir)
        
        # going again up the tree, importing all required files, including imported
        # libraries
        playful_dir = True
        current_dir = path
        
        while playful_dir:
            instance = Directory(current_dir,root_dir)
            try: imports = instance.get_imports()
            except Exception as e :
                print("warning:",e,"\n")
            self.rt_directories.append(instance)
            self.rt_directories += imports
            new_dir = os.path.abspath(current_dir+os.sep+"..")
            playful_dir = "__playful__" in [f for f in os.listdir(new_dir)]
            if playful_dir : current_dir=new_dir
            
        # rt_directories is ordered (top down trees),
        # so executing on_start.py should follow this order
        self.rt_directories.reverse()

        
    def get_execution_trail(self):
        
        class Trail:

            __slots__ = ["rt","py","py_dirs",
                         "resources","globals_",
                         "on_start","on_stop"]
            
            def __init__(self):
                
                self.rt = []
                self.py = []
                self.py_dirs = []
                self.resources = []
                self.globals_ = []
                self.on_start = []
                self.on_stop = []
                
            def __str__(self):
                all_files = [self.rt+
                              self.py+
                              self.py_dirs+
                              self.resources+
                              self.globals_+
                              self.on_start+
                              self.on_stop]
                return " ".join(all_files)
            
        trail = Trail()
        
        for directory in self.rt_directories:
            pys,rts,py_dirs = directory.get_rt_files()
            trail.py.extend(pys)
            trail.rt.extend(rts)
            trail.py_dirs.extend(py_dirs)
            special_files_paths = directory.get_special_files_paths()
            for file_path,variables in zip( special_files_paths,
                                            [ trail.globals_,
                                              trail.resources,
                                              trail.on_start,
                                              trail.on_stop ] ):
                if file_path : variables.append(file_path)
                
        return trail
