# Copyright 2019 Max Planck Gesellschaft
# Author: Vincent Berenz


import os

# note : __init__.py files automatically created if not there

class Directory(object):
    
    IMPORTS = set()

    __slots__ = ["path","root_path","name"]

    
    def __init__(self,path,root_path):
        
        self.path = path
        self.root_path = root_path
        self.name = os.path.basename(path)
        if not os.path.isfile(path+os.sep+"__init__.py"):
            open(path+os.sep+"__init__.py","a")

            
    def get_rt_files(self):
        
        pys,rts,py_directories = [],[],[]
        subdirs = [d for d in os.listdir(self.path)
                   if os.path.isdir(self.path+os.sep+d)]
        
        if "py" in subdirs:
            for root,dirs,files in os.walk(self.path+os.sep+"py"):
                # creating __init__.py files in py folders
                if not os.path.isfile(root+os.sep+"__init__.py"):
                    open(root+os.sep+"__init__.py","a")
                pys.extend([root+os.sep+f for f in files if f.endswith("_play.py")])
                py_directories.append(root)
                
        if "play" in subdirs:
            for root,dirs,files in os.walk(self.path+os.sep+"play"):
                rts.extend([root+os.sep+f
                            for f in files if f.endswith(".play")])
                
        return pys,rts,py_directories

    
    def _get_file_path(self,file_name):
        
        if os.path.isfile(self.path+os.sep+"config"+os.sep+file_name):
            return self.path+os.sep+"config"+os.sep+file_name
        return None

    
    def get_special_files_paths(self):
        
        return [ self._get_file_path(file_name)
                 for file_name in ["globals.py",
                                   "resources.txt",
                                   "on_start.py",
                                   "on_stop.py",
                                   "imports.txt"] ]

    
    # returns instances of Directory
    # also add them to python path
    def get_imports(self):
        
        special_files = self.get_special_files_paths()
        imports_file = None
        for file_path in special_files:
            if file_path and file_path.endswith("imports.txt"):
                imports_file = file_path
                break
            
        if imports_file is None :
            return []
        
        try :
            with open(imports_file,"r") as f :
                lines = f.readlines()
        except Exception as e :
            raise Exception("failed to read file: "+imports_file+": "+str(e))
        
        instances = []
        
        for line in lines:
            line = line.strip()
            if line:
                if(not line.startswith('#')):
                    path =  os.path.abspath(self.root_path+os.sep+line)
                    if not os.path.isdir(path):
                        raise Exception("failed to find directory "+line
                                        +" in "+self.root_path
                                        +" (as imported in "+imports_file+")")
                    if path not in self.__class__.IMPORTS:
                        instance = self.__class__(path,self.root_path)
                        instances.append(instance)
                        self.__class__.IMPORTS.add(path)
                        
        extended_instances = []
        
        for instance in instances :
            extended_instances = extended_instances + instance.get_imports()
            
        instances = instances + extended_instances
        
        return instances
