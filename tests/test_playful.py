import unittest,os,time,threading

from playful.component.resources_manager import *
from playful.resources.resources import Resources
from playful.memory.memory import Memory
from playful.terminal.terminal import execute, stop


class PLAYFUL_TESTCASE(unittest.TestCase):

    
    def setUp(self):
        this_file_path = os.path.realpath(__file__)
        this_file_name = os.path.basename(this_file_path)
        self.test_folder = this_file_path[:-len(this_file_name)]
        self.test_folder = os.path.abspath(self.test_folder+os.sep+"test_projects"+os.sep)
        
    def tearDown(self):
        Memory.reset()
        Resources.reset()

    
    def get_dir(self,folder):
        return os.path.abspath(self.test_folder+os.sep+folder)
    
    
    def test_resources(self):

        class _Pseudo:
            def __init__(self,name):
                self.name = name
            def __str__(self):
                return str(self.name)
        
        # asking for resource
        componentA = _Pseudo("A")
        ask_for_resource(componentA,"test_resource")

        # test: resource attributed to A
        Resources.attribute_resources( [componentA] )
        received = ask_for_resource(componentA,"test_resource")
        self.assertEqual(received,True)

        # test: we know A has resource
        self.assertEqual( is_having_resource(componentA, "test_resource"), True)

        # test: we also know A has resource
        self.assertEqual ( "test_resource" in resources_used(componentA) , True )
        
        # A has resource, B should be denied
        componentB = _Pseudo("B")
        ask_for_resource(componentB,"test_resource")
        Resources.attribute_resources( [componentA,componentB] )
        received = ask_for_resource(componentB,"test_resource")
        self.assertEqual( received, False )

        # A release the resource and stop asking for resource,
        # so B should get it
        release_resource(componentA,"test_resource")
        stop_asking_for_resource(componentA,"test_resource")
        Resources.attribute_resources( [componentA,componentB] )
        received = ask_for_resource(componentB,"test_resource")
        self.assertEqual( received, True )

        # A highjacking the resource, so gets denied to B
        take_resource(componentA,"test_resource")
        Resources.attribute_resources( [componentA,componentB] )
        received = ask_for_resource(componentB,"test_resource")
        self.assertEqual( received, False )

        # B did not release the resource, though
        self.assertEqual( is_having_resource(componentB, "test_resource"), True)

        # B releases the resource, so goes to A
        release_resource(componentB,"test_resource")
        Resources.attribute_resources( [componentA,componentB] )
        received = ask_for_resource(componentB,"test_resource")
        self.assertEqual( received, False )
        received = ask_for_resource(componentA,"test_resource")
        self.assertEqual( received, True )

        # A untake and release the resource
        untake_resource(componentA,"test_resource")
        release_resource(componentA,"test_resource")

        # A and B both asking resource
        ask_for_resource(componentA,"test_resource")
        ask_for_resource(componentB,"test_resource")
        # A is first priority (order of the list)
        Resources.attribute_resources( [componentA,componentB] )
        # so A gets the resource
        received = ask_for_resource(componentB,"test_resource")
        self.assertEqual( received, False )
        received = ask_for_resource(componentA,"test_resource")
        self.assertEqual( received, True )
        # A releases the resource
        release_resource(componentA,"test_resource")
        # B is first priority (order of the list)
        Resources.attribute_resources( [componentB,componentA] )
        # so B gets the resource
        received = ask_for_resource(componentB,"test_resource")
        self.assertEqual( received, True )
        received = ask_for_resource(componentA,"test_resource")
        self.assertEqual( received, False )
        

    def test_memory(self):

        class A:
            def __init__(self,value):
                self.value = value

        class B:
            def __init__(self,
                         value1,
                         value2):
                self.value1 = value1
                self.value2 = value2

        a1 = A(1)
        a2 = A(2)
        b1 = B(1,1)
        b2 = B(2,2)

        # set instance of A to memory and
        # getting it back
        Memory.set(a1)
        a1_ = Memory.get("A")
        self.assertEqual(a1.value,a1_.value)

        # Memory should report a1 as new item
        new_items = Memory.new_items()
        self.assertEqual(len(new_items),1)
        # new items should be [ (classname,item_id) ]
        classname,item_id = new_items[0]
        # the item is of class A
        self.assertEqual(classname,"A")
        # we did not give any id to the item, so should be default
        self.assertEqual(item_id,Memory.DEFAULT_ID)

        # new items have just been consumed, so empty now 
        new_items = Memory.new_items()
        self.assertEqual(len(new_items),0)

        # set a new instance of A, still not id (so default id),
        # and should overwrite current instance a1
        Memory.set(a2)
        a2_ = Memory.get("A")
        self.assertEqual(a2_.value,a2.value)
        
        # previous action was not a new item, as an instance
        # of A with same id was already there
        new_items = Memory.new_items()
        self.assertEqual(len(new_items),0)

        # adding 2 items with different ids, so they do not
        # overwrite each others
        Memory.set(b1,1)
        Memory.set(b2,2)
        new_items = Memory.new_items()
        self.assertEqual(len(new_items),2)

        # changing attributes
        b1_ = Memory.get("B",1)
        b1_.value1 = 3
        Memory.set(b1_,1)
        b1__ = Memory.get("B",1)
        self.assertEqual(b1__.value1,3)

        # getting None when requesting non
        # existing items
        b3 = Memory.get("B")
        self.assertEqual(b3 is None,True)
        b4 = Memory.get("B",3)
        self.assertEqual(b4 is None,True)
        b5 = Memory.get("C")
        self.assertEqual(b5 is None,True)

        # getting all works
        bs = Memory.get_all("B")
        self.assertEqual(len(bs),2)
        self.assertEqual(1 in bs.keys(),True)
        self.assertEqual(2 in bs.keys(),True)
        self.assertEqual(3 in bs.keys(),False)

        # changing attribute value
        # directly in the memory
        # (because another thread could be changing
        # another attribute async)
        changed = Memory.setattr("B","value1",8,1)
        self.assertEqual(changed,True)
        changed = Memory.setattr("B","value2",9,1)
        self.assertEqual(changed,True)
        b6 = Memory.get("B",1)
        self.assertEqual(b6.value1,8)
        self.assertEqual(b6.value2,9)

        # deleting b1
        Memory.delete("B",1)
        bs = Memory.get_all("B")
        # so only b2 remaining
        self.assertEqual(len(bs),1)
        # deleting b2
        Memory.delete("B",2)
        bs = Memory.get_all("B")
        # so nobody left
        self.assertEqual(len(bs),0)
        # 2 items have been deleted
        deleted = Memory.deleted_items()
        self.assertEqual(len(deleted),2)
        # deleted has been purged
        deleted = Memory.deleted_items()
        self.assertEqual(len(deleted),0)
        

    def _start(self,folder):
        self._thread = threading.Thread( target=execute,
                                         args=(folder,) )
        self._thread.start()

        
    def _stop(self):
        stop()
        self._thread.join()

        
    def test_simple_node(self):

        folder = self.get_dir("test_simple_node")
        self._start(folder)
        time.sleep(0.1)
        self._stop()
        arg1 = Memory.get("arg1")
        arg2 = Memory.get("arg2")
        self.assertEqual(arg1,"1")
        self.assertEqual(arg2,"2")

    def test_args_node(self):

        folder = self.get_dir("test_args_node")
        self._start(folder)
        time.sleep(0.1)
        self._stop()
        arg1 = Memory.get("arg1")
        arg2 = Memory.get("arg2")
        self.assertEqual(arg1,"-1")
        self.assertEqual(arg2,"-2")

    def test_two_nodes(self):

        folder = self.get_dir("test_two_nodes")
        self._start(folder)
        time.sleep(0.1)
        self._stop()
        arg1 = Memory.get("arg1")
        arg2 = Memory.get("arg2")
        arg3 = Memory.get("arg3")
        arg4 = Memory.get("arg4")
        self.assertEqual(arg1,"1")
        self.assertEqual(arg2,"-2")
        self.assertEqual(arg3,"3")
        self.assertEqual(arg4,"-4")

    def test_simple_tree(self):

        folder = self.get_dir("test_simple_tree")
        self._start(folder)
        time.sleep(0.1)
        self._stop()
        arg1 = Memory.get("arg1")
        arg2 = Memory.get("arg2")
        arg3 = Memory.get("arg3")
        arg4 = Memory.get("arg4")
        arg5 = Memory.get("arg5")
        arg6 = Memory.get("arg6")
        self.assertEqual(arg1,"1")
        self.assertEqual(arg2,"2")
        self.assertEqual(arg3,"3")
        self.assertEqual(arg4,"-4")
        self.assertEqual(arg5,"5")
        self.assertEqual(arg6,"-6")
        
    def test_priorities(self):
        
        folder = self.get_dir("test_priorities")
        self._start(folder)
        time.sleep(0.1)
        self._stop()
        arg = Memory.get("arg")
        self.assertEqual(arg,"p2")

    def test_conditional(self):
        
        folder = self.get_dir("test_conditional")
        self._start(folder)
        time.sleep(0.1)
        self._stop()
        arg = Memory.get("arg")
        self.assertEqual(arg,"p1")

    def test_higher_conditional(self):
        
        folder = self.get_dir("test_higher_conditional")
        self._start(folder)
        Memory.set("never_true_called",False)
        time.sleep(0.1)
        self._stop()
        arg = Memory.get("arg")
        never_true_called = Memory.get("never_true_called")
        self.assertEqual(never_true_called,True)
        self.assertEqual(arg,"p1")
        
    def test_dynamic_priority(self):
        
        folder = self.get_dir("test_dynamic_priority")
        self._start(folder)
        Memory.set("scoring",False)
        time.sleep(1.0)
        self._stop()
        called = Memory.get("scoring")
        self.assertEqual(called,True)
        arg = Memory.get("arg")
        self.assertEqual(arg,"p2")

    def test_dynamic_priority_2(self):
        
        folder = self.get_dir("test_dynamic_priority_2")
        self._start(folder)
        Memory.set("changing",False)
        time.sleep(0.1)
        arg = Memory.get("arg")
        self.assertEqual(arg,"p1")
        time.sleep(0.5)
        self._stop()
        called = Memory.get("changing")
        self.assertEqual(called,True)
        arg = Memory.get("arg")
        self.assertEqual(arg,"p2")

        
    def test_targeting(self):

        folder = self.get_dir("test_targeting")
        self._start(folder)
        Memory.set("created",False)
        time.sleep(0.5)
        self._stop()
        created = Memory.get("created")
        self.assertEqual(created,True)
        target_value = Memory.get("target_value")
        self.assertEqual(target_value,5)

    def test_two_targets(self):

        folder = self.get_dir("test_two_targets")
        self._start(folder)
        Memory.set("created",False)
        Memory.set("created_2",False)
        Memory.set("created_3",False)
        time.sleep(0.5)
        self._stop()
        created = Memory.get("created")
        self.assertEqual(created,True)
        created = Memory.get("created_2")
        self.assertEqual(created,True)
        created = Memory.get("created_3")
        self.assertEqual(created,True)
        target_value = Memory.get("target_value")
        self.assertEqual(target_value,3)

    def test_target_tree(self):
        Memory.set("arg1","-1")
        Memory.set("arg2","-2")
        Memory.set("target_value",10)
        folder = self.get_dir("test_target_tree")
        self._start(folder)
        Memory.set("created",False)
        time.sleep(0.3)
        self._stop()
        created = Memory.get("created")
        self.assertEqual(created,True)
        target_value = Memory.get("target_value")
        self.assertEqual(target_value,5)
        arg1 = Memory.get("arg1")
        arg2 = Memory.get("arg2")
        self.assertEqual(arg1,"1")
        self.assertEqual(arg2,"2")

    def test_two_targets_tree(self):
        Memory.set("instance_value",10)
        Memory.set("other_instance_value",10)
        folder = self.get_dir("test_two_targets_tree")
        self._start(folder)
        Memory.set("created",False)
        time.sleep(0.3)
        self._stop()
        created = Memory.get("created")
        self.assertEqual(created,True)
        instance_value = Memory.get("instance_target")
        self.assertEqual(instance_value,12)
        other_instance_value = Memory.get("other_instance_target")
        self.assertEqual(other_instance_value,-8)

    def test_state_machines(self):
        folder = self.get_dir("test_state_machines")
        self._start(folder)
        time.sleep(0.15)
        self.assertEqual(Memory.get("arg1"),"a")
        time.sleep(0.3)
        self.assertEqual(Memory.get("arg1"),"b")
        time.sleep(0.3)
        self.assertEqual(Memory.get("arg1"),"c")
        time.sleep(0.3)
        self._stop()
        self.assertEqual(Memory.get("arg1"),"c")
        created = Memory.get("created")

    def test_exception(self):
        folder = self.get_dir('test_exception')
        self._start(folder)
        Memory.set("test_resource_exit_p2",False)
        time.sleep(0.3)
        self._stop()
        self.assertEqual(Memory.get("test_resource_exit_p2"),True)

    def test_local_python(self):
        folder = self.get_dir('test_local_python')
        self._start(folder)
        Memory.set("local",None)
        time.sleep(0.3)
        self._stop()
        self.assertEqual(Memory.get("local"),"l1")

        

        
if __name__ == '__main__':
        unittest.main()
