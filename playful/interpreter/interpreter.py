# Copyright 2019 Max Planck Gesellschaft
# Author: Vincent Berenz


from .word import Word


def playful_to_python(rt_file):

    
    class block:

        __slots__ = ["name","line","code",
                     "kwargs","type_"]
        
        def __init__( self,
                      name,
                      line,
                      code,
                      kwargs={},
                      type_="fractal" ):

            self.type_ = type_
            self.name = name
            self.line = line
            self.code = code
            self.kwargs = kwargs
            
        def __str__(self):
            
            return " ".join([str(a)
                             for a in [self.name,self.line,self.code]])

        
    def get_block(content,line_number):
        
        content = [c for c in content if '#' not in c]
        
        def valid_targeted_behavior(line):
            if ":" not in line :
                return False
            targeted = line[:line.index(":")]
            targeted = targeted.split(" ")
            targeted = [t for t in targeted if t!=""]
            if len(targeted)!=2 :
                return False
            if targeted[0].strip()=="targeting" :
                return True
            
        def parse_kwargs(kwargs_str):
            if not kwargs_str :
                return {}
            kwargs_str = kwargs_str.split(";")
            kwargs = {}
            for a in kwargs_str :
                if not "=" in a :
                    raise Exception(str( rt_file+
                                         ":"+content+
                                         ":"+line_number+
                                         ": syntax error in arguments "+
                                         "definition, '=' missing ? " ) )
                try :
                    arg_name = a[:a.index("=")].strip()
                    arg_val = a[a.index("=")+1:].strip()
                    kwargs[arg_name]=eval(arg_val,{},{})
                except Exception as e :
                    raise Exception( str("failed to parse"+
                                         " and evaluate arguments:\n"+str(e)) )
            return kwargs
        
        intro = content[line_number]
        intro = intro.strip()
        kwargs_str = None
        
        if ":" in intro :
            name = intro[:intro.index(':')]
            type_ = "fractal"
            if intro[intro.index(':')+1:].strip()=="scheme" :
                type_="scheme"
                
        else :
            name = ""
        
        if "|" in name : 
            kwargs_str = name[name.index("|")+1:]
            name = name[:name.index("|")]
            
        name = name.strip()
        
        if kwargs_str :
            kwargs_str = kwargs_str.strip()
            
        try : 
            kwargs = parse_kwargs(kwargs_str)
        except Exception as e :
            raise Exception("failed to parse script arguments: "+
                            kwargs_str+"\n"+str(e))
        
        code = []
        line_number+=1
        
        while ( line_number<len(content)
                and ( (":" not in content[line_number])
                      or (valid_targeted_behavior(content[line_number]))) ) :
            stripped = content[line_number].strip()
            if not stripped.startswith("#"):
                stripped = stripped.replace("\t","")
                stripped = stripped.replace("\n","")
                if stripped != "": code.append(stripped)
            line_number+=1
            
        if len(code)==0 :
            return None,False
        
        b = block(name,line_number,code,kwargs=kwargs,type_=type_)
        
        if line_number==len(content) :
            return b,False
        
        return b,line_number
    
    if isinstance(rt_file,str):
        with open(rt_file,"r") as f:
            content = f.readlines()
    else :
        content =  rt_file
        
    content.insert(0,"\n")
    content = [c.strip() for c in content]
    content = [c for c in content if not c.startswith('#')]
    line_number = 0
    
    while ":" not in content[line_number]:
        line_number+=1
        
    blocks = []
    
    while line_number and line_number<len(content):
        b,new_line_number = get_block(content,line_number)
        if b is None :
            raise Exception("failed to read "+rt_file
                            +", error at line "+str(line_number)+" (no content ?)")
        line_number = new_line_number
        blocks.append(b)
    r = []
    
    for b in blocks:
        r.append( Word(b.name,
                       b.type_,
                       rt_file,
                       b.line,
                       b.code,
                       None,
                       kwargs=b.kwargs) )
        
    return r







