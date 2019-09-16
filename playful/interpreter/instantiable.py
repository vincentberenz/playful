from ..orchestration.statement import Statement
from ..interpreter.parsing import parse_code_line
from ..memory.memory import Memory

class Instantiable_fractal:
    
    def __init__( self,
                  name,
                  tries_,
                  evaluation_str,
                  score_calculators_strs,
                  state_transition_strs,
                  **global_kwargs ):
        
        locs = locals()
        for l in locs :
            setattr(self,l,locs[l])
            
    def instantiate(self,
                    scheme_type,
                    scheme_id):
        
        return instantiate_fractal( self.name,
                                    self.tries_,
                                    scheme_type,
                                    scheme_id,
                                    self.evaluation_str,
                                    self.score_calculators_strs,
                                    self.state_transition_strs,
                                    **self.global_kwargs )


def instantiate_fractal( name,
                         tries_,
                         scheme_type,
                         scheme_id,
                         evaluation_str,
                         score_calculator_strs,
                         state_transition_strs,
                         **global_kwargs ):

    set_commit = None
    
    def update_kwargs(global_kwargs,local_kwargs):
        r = {k:v for k,v in local_kwargs.items()}
        for k,v in local_kwargs.items():
            try:
                if v in global_kwargs :
                    r[k]=global_kwargs[v]
            except : pass # certainly v is unhashable
        return r
    
    is_component = False
    
    if all([a in global_kwargs for a in ["ros","node","package"]]) and global_kwargs["ros"]:
        instance_kwargs = {k:global_kwargs[k]
                           for k in list(global_kwargs.keys())
                           if k in ["ros","node","package","resources","rosargs"]}
        is_component = True
        
    else:
        try : 
            word_ = tries_["component"][name]
            class_ = word_.class_
            is_component = True
        except : 
            try :
                word_ = tries_["fractal"][name]
                class_ = Statement
            except :
                raise Exception("\nplayful interpreter error: '"+
                                str(name)+"' is not a known node\n")

        default_kwargs = word_.kwargs
        instantiate_kwargs = {k:v for k,v in default_kwargs.items()}
        
        for k in default_kwargs:
            if k in global_kwargs : instantiate_kwargs[k]=global_kwargs[k]
            
        instance = class_(**instantiate_kwargs)
        
    instance._set_name(name)
    
    instance.set_evaluation_str(evaluation_str,**global_kwargs)
    instance.set_score_calculator_strs(score_calculator_strs,**global_kwargs)
    instance.set_state_transition_strs(state_transition_strs,**global_kwargs)
    instance.set_scheme_id_and_scheme_type(scheme_id,scheme_type)
    
    if is_component : return instance
    all_targets = []
    
    for line_code in word_.code:
        line_code = line_code.strip()
        name,type_,target,evaluation_str,score_calculator_strs,state_transitions_strs,local_kwargs = parse_code_line(line_code)
        updated_kwargs = update_kwargs(instantiate_kwargs,local_kwargs)
        if target : 
            instance.add_targeted_behavior(name,
                                           target,
                                           Instantiable_fractal(name,
                                                                tries_,
                                                                evaluation_str,
                                                                score_calculator_strs,
                                                                state_transition_strs,
                                                                **updated_kwargs))
            items = Memory.get_all(target)
            if items is not None:
                items = [(target,item_id) for item_id in items.keys()]
            else :
                items = []
            all_targets += items
        else : 
            sub_instance = instantiate_fractal(name,tries_,
                                               scheme_type,
                                               scheme_id,
                                               evaluation_str,
                                               score_calculator_strs,
                                               state_transitions_strs,
                                               **updated_kwargs)
            if type_ == "behavior" :
                instance.add_behavior(sub_instance)
            else :
                instance.add_state(sub_instance)
                
    if all_targets:
        instance.manage_template_behaviors_instances(list(all_targets),[])
        
    return instance
