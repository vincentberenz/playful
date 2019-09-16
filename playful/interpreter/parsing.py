# Copyright 2019 Max Planck Gesellschaft
# Author: Vincent Berenz


# return name,type ("behavior" or "state"),target, evaluation_str, score_calculator_strs (list), state_transitions (list), **kwargs
def parse_code_line(code_line):
    
    code_line = code_line.replace("\t"," ")
    
    def separate_kwargs(line):
        
        if "|" in line :
            au = line[:line.index("|")].strip()
            args = line[line.index("|")+1:]
            args = args.split(";")
            kwargs = {}
            for a in args :
                if not "=" in a :
                    raise Exception(line+
                                    ": syntax error in arguments definition, '=' missing ? ")
                try :
                    arg_name = a[:a.index("=")].strip()
                    arg_val = a[a.index("=")+1:].strip()
                    try :
                        kwargs[arg_name]=eval(arg_val,{},{})
                    except :
                        kwargs[arg_name]=str(arg_val)
                except :
                    raise Exception("failed to parse arguments : "+str(a))
                
            return au,kwargs
        
        return line.strip(),{}
    
    core,kwargs = separate_kwargs(code_line)
    seps = core.split(',')
    seps = [s.strip() for s in seps if s!='']
    type_ = "behavior"
    target = None
    
    if ':' in seps[0]:
        if seps[0].startswith("state") :
            type_="state"
        elif seps[0].startswith("targeting"):
            target = seps[0][9:seps[0].index(":")].strip()
            name = seps[0][seps[0].index(":")+1:].strip()
            
    else :
        name = seps[0]
        
    evaluation_str = None
    score_calculator_strs = []
    state_transitions_strs = []
    
    for s in seps[1:]:
        if s.startswith("while ") :
            evaluation_str=s[6:]
        elif s.startswith("priority of ") :
            score_calculator_strs.append(s[12:])
        elif s.startswith("switch to ") :
            type_="state"
            state_transitions_strs.append(s)
        else :
            raise Exception("\nplayful interpreter error: could not understand : "+
                            str(s)+"\n")
        
    return name,type_,target,evaluation_str,score_calculator_strs,state_transitions_strs,kwargs
