# Copyright 2019 Max Planck Gesellschaft
# Author: Vincent Berenz


import curses,threading,time,traceback


class _display_slot(object):
    
    def __init__(self,display_str,duration):
        
        self.display_str = display_str
        self.duration = duration
        self.timestart = time.time()

        
class Display(object):
    
    _time = None
    _slots = None
    _report = []
    _lock = None
    _screen = None
    _should_exit = False
    _monitor_exit_thread = None
    _error = None
    _error_lock = None
    _initiated = False
    
    @classmethod
    def init(cls,slots=15,frequency=5):
        cls._initiated = True
        cls._time = (1.0/frequency)
        cls._slots = {}
        cls._screen = curses.initscr()
        cls._lock = threading.Lock()
        cls._error_lock = threading.Lock()
        curses.noecho()
        curses.curs_set(0)
        curses.start_color()
        curses.use_default_colors()
        curses.init_pair(1,curses.COLOR_GREEN,-1)
        curses.init_pair(2,curses.COLOR_BLUE,-1)
        cls._screen.keypad(1)       
        cls._monitor_exit_thread = threading.Thread(target=cls.monitor_exit)
        cls._monitor_exit_thread.setDaemon(True)
        cls._monitor_exit_thread.start()
        
    @classmethod
    def monitor_exit(cls):
        while not cls._should_exit:
            event = cls._screen.getch()
            if event == ord("q"): cls._should_exit=True
            
    @classmethod
    def set_report(cls,report):
        with cls._lock: cls._report = report
        
    @classmethod
    def console(cls,display_id,display_str,duration=None):
        display_str = str(display_str)
        if not cls._initiated : 
            print(display_str)
            return
        try : 
            if not duration : duration=float("+inf")
            with cls._lock : 
                try :
                    cls._slots[display_id].display_str = display_str
                    cls._slots[display_id].duration = duration
                except : cls._slots[display_id] = _display_slot(display_str,duration)
        except Exception as e :
            trace =  traceback.format_exc() 
            with cls._error_lock : cls._error = str(trace)+"\n"+str(e)
            
    @classmethod
    def unconsole(cls,display_id):
        if not cls._initiated: return
        with cls._lock:
            try : del cls._slots[display_id]
            except : pass
            
    @classmethod
    def refresh(cls):
        
        def _update_slots():
            r = []
            t = time.time()
            to_remove = []
            with cls._lock:
                for slot_id,slot in cls._slots.items():
                    if t-slot.timestart > slot.duration : to_remove.append(slot_id)
                    else : r.append(slot.display_str)
                for e in to_remove : del cls._slots[e]
            return r
        
        if cls._should_exit :
            cls._screen.clear()
            cls._screen.addstr("exiting ...")
            
        cls._screen.clear()
        
        if cls._error :
            cls._screen.addstr("display error : \n\n"+
                               str(cls._error)+"\n\n(press 'q' to exit)")
        else :
            try : 
                total_report = cls._report + ["","\n[console]"] +_update_slots()
                for r in total_report:
                        if "[running]" in r and not "denied" in r : 
                            if "resources" in r : 
                                try :
                                    cls._screen.addstr(r+"\n",curses.color_pair(1))
                                except :
                                    pass
                            else:
                                try :
                                    cls._screen.addstr(r+"\n",curses.color_pair(2))
                                except :
                                    pass
                        else :
                            try :
                                cls._screen.addstr(r+"\n")
                            except : pass
            except Exception as e :
                trace =  traceback.format_exc() 
                with cls._error_lock: cls._error = str(trace)+"\n"+str(e)
                
        cls._screen.refresh()
        
    @classmethod
    def exit(cls):
        curses.endwin()
        if cls._error :
            print("\ndisplay error:\n\n"+cls._error+"\n")
        
    @classmethod
    def get_error(cls) :
        return cls._error
    
    @classmethod
    def stopped(cls): return cls._should_exit


    
class open_display(object):
    
    def __init__(self,slots=15,frequency=10):
        self._slots = slots
        self._frequency = frequency
        
    def __enter__(self):
        Display.init(slots=self._slots,frequency=self._frequency)
        return Display
    
    def __exit__(self,t,value,traceback):
        Display.exit()
        
    def stopped(self): return Display.stopped()
