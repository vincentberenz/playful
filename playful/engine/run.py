# Copyright 2019 Max Planck Gesellschaft
# Author: Vincent Berenz


import threading,os,time,sys

from ..interpreter.instantiable import instantiate_fractal
from ..component.spineable import Spineable
from ..memory.memory import Memory
from ..resources.resources import Resources
from ..interpreter.lib import Lib
from ..display.display import open_display

class running:

    running = False
    similarity_threshold = 0.9
    error = None

    
class fIntrospection:
    
    activated = []
    lock = threading.Lock()
    
    @classmethod 
    def _set(cls,activated):
        with cls.lock:
            cls.activated = activated
            
    @classmethod
    def get(cls):
        with cls.lock:
            return [a for a in cls.activated]
        

def run( main_frequency=40.0,
         print_report = False,
         share_report=False,
         tree_representation=False,
         report_frequency=2.0,
         similarity_threshold=0.9,
         exit_on_q=True):
    
    running.similarity_threshold = similarity_threshold
    
    main_fractal = instantiate_fractal( "program",
                                        Lib.tries,
                                        None,
                                        None,
                                        None,
                                        ['1'],
                                        [] )
    
    running.running = True
    
    def detect_stop_signal_press():
        while running.running : 
            try: 
                key = input() # may not work from sh script
                if key=='q': running.running = False
            except : pass
            time.sleep(0.05)
            
    def detect_quit_file():
        stop_file = os.getcwd()+os.sep+"stop.txt"
        while running.running :
            if os.path.isfile(stop_file):
                os.remove(stop_file)
                running.running = False
            time.sleep(0.1)
            
    def get_errors():
        errors = main_fractal.get_errors()
        if errors and running.running :
            running.error = '\n'.join(errors)
            if not print_report :
                # if print report, this is blocked by curses module.
                # so printing delayed to curses module closed.
                print('\n* playful runtime error *\n'+running.error) 
            running.running = False
            
    def report(frequency):
        activated = []
        main_fractal.introspection(activated)
        fIntrospection._set(activated)
        with open_display(frequency=frequency) as display:
            while running.running and not display.stopped():
                report = ['(press q to exit)\n[tree]']+main_fractal.report()
                display.set_report(report)
                display.refresh()
                if share_report : Memory.set("report",report,in_report=False)
                time.sleep(1.0/frequency)
        running.running = False
        if running.error :
            print('\nruntime error\n'+str(running.error)+"\n")
            
    if print_report:
        _report_thread = threading.Thread(target=report,args=(report_frequency,))
        _report_thread.setDaemon(True)
        _report_thread.start()
        
    else :
        if exit_on_q:
            exit_thread = threading.Thread(target=detect_stop_signal_press)
            exit_thread.setDaemon(True)
            exit_thread.start()
        
    spin = Spineable()
    
    try:
        while running.running:
            get_errors()
            main_fractal.manage_template_behaviors_instances(Memory.new_items(),
                                                             Memory.deleted_items())
            main_fractal.iterate(parent_run=True)
            components = main_fractal.get_ordered_components()
            Resources.attribute_resources(components)
            spin.spin(main_frequency)
            
    except KeyboardInterrupt:
        running.running=False

    if print_report :
        _report_thread.join()
    else :
        if exit_on_q:
            exit_thread.join()
    
    main_fractal.iterate(parent_run=False)
    
    survivor = None
    kill_time = 1
    killed = False
    start = time.time()
    
    while main_fractal.is_running() and not killed: 
        components = main_fractal.get_ordered_components()
        active_components = [c for c in components if c.is_running()]
        if (not killed) and time.time()-start>5:
            for c in active_components:
                c.kill()
            killed=True
        time.sleep(0.02)
        
    components = main_fractal.get_ordered_components()
    active_components = [c for c in components if c.is_running()]
    
    Resources.stop()
    Resources.reset()
