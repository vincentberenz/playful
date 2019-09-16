import playful


class local_component(playful.Node):


    def __init__(self,local_value=None):

        self.local_value = local_value
    
    
    def execute(self):

        while not self.should_pause():

            playful.Memory.set("local",self.local_value)

            self.spin(30)


def local_conditional():
    
    return True
