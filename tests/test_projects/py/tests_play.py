import playful,time


class test1(playful.Node):

    def __init__(self,arg1="1",arg2="2"):
        
        self.arg1 = arg1
        self.arg2 = arg2
    

    def execute(self):

        done = False

        while not self.should_pause():

            if not done:
                playful.Memory.set("arg1",self.arg1)
                playful.Memory.set("arg2",self.arg2)
                done = True

            self.spin(20)


            
class test2(playful.Node):

    def __init__(self,arg3="3",arg4="4"):
        
        self.arg3 = arg3
        self.arg4 = arg4
    

    def execute(self):

        done = False

        while not self.should_pause():

            if not done:
                playful.Memory.set("arg3",self.arg3)
                playful.Memory.set("arg4",self.arg4)
                done = True

            self.spin(20)

            
class test3(playful.Node):

    def __init__(self,arg5="5",arg6="6"):
        
        self.arg5 = arg5
        self.arg6 = arg6
    

    def execute(self):

        done = False

        while not self.should_pause():

            if not done:
                playful.Memory.set("arg5",self.arg5)
                playful.Memory.set("arg6",self.arg6)
                done = True

            self.spin(20)

            
class test_resource(playful.Node):

    def __init__(self,arg="0"):
        
        self.arg = arg

    def execute(self):

        while not self.should_pause():

            if self.ask_for_resource("test_resource"):
                playful.Memory.set("arg",self.arg)

            else:
                self.release_all_resources()    

            self.spin(20)

        playful.Memory.set("test_resource_exit_"+str(self.arg),True)
            

def never_true():

    return False



def scoring(value=2):

    playful.Memory.set("scoring",True)
    
    return value

    
    

class _changing:
    start = None
    
def changing(v1=0.5,v2=1.5,time_wait=0.3):

    playful.Memory.set("changing",True)
    
    if _changing.start is None:
        _changing.start = time.time()

    t = time.time()

    if t - _changing.start < time_wait:
        return v1

    return v2



class instance :

    def __init__(self,value):
        self.value = value


class other_instance:

    def __init__(self,value):
        self.value = value
        
        
class test_target(playful.Node):

    def __init__(self,no_resource=False,
                 memory_key="target_value"):
        self.no_resource = no_resource
        self.memory_key = memory_key
    
    def execute(self):
        
        while not self.should_pause():

            playful.Memory.set("created",True)

            target = self.get_target()

            if target is not None:
                playful.Memory.set("created_"+str(target.value),True)
            
            if self.no_resource or self.ask_for_resource("target_resource"):
                
                if target is not None:
                    playful.Memory.set(self.memory_key,target.value)

            else :

                self.release_all_resources()
            
            self.spin(30)


            
class set_instance(playful.Node):

    
    def __init__(self,value=None,other=False):
        
        self.value = value
        self.other = other
    
    def execute(self):

        if not self.other:
            i = instance(self.value)
        else:
            i = other_instance(self.value)
            
        while not self.should_pause():
            playful.Memory.set(i,id(self))
            self.spin(30)

            
def instance_value(target=None,
                   default_value=-1):
    
    if target is not None:
        return target.value
    return default_value
    

class _transit:
    start = None

def transit(state=None,stamp=None):
    if _transit.start is None:
        _transit.start = time.time()
    if time.time()-_transit.start > stamp:
        return True
    return False
    

class _raise_exception:
    start = None

def raise_exception(delay=0.5):

    if _raise_exception.start is None:
        _raise_exception.start = time.time()

    if time.time()-_raise_exception.start > delay :
        return 1 / 0

    return True



class turn_switcher(playful.Node):

    current_turn = "a"

    def __init__(self,period=2.0):
        self.period = period

    def execute(self):

        last_time = time.time()
        
        while not self.should_pause():

            t = time.time()
            if t-last_time > self.period:
                if self.__class__.current_turn == "a":
                    self.__class__.current_turn = "b"
                else :
                    self.__class__.current_turn = "a"
                last_time = t

            self.spin(40)


def switch_turn(go_to=None):

    if turn_switcher.current_turn==go_to:
        return True

    return False
