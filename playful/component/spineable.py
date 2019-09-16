# Copyright 2019 Max Planck Gesellschaft
# Author: Vincent Berenz


import collections,time

class Spineable(object):

    
    def __init__(self, **kwargs):
        
        self._previous_spin = None
        self._accumulated_spin = 0
        self._s_frequency_queue = collections.deque(
            [time.time() for _ in range(10)], 10)
        self._s_frequency = 0

        
    def reset(self):
        
        self._previous_spin = None
        self._accumulated_spin = 0

        
    def get_frequency(self):

        return self._s_frequency

    
    def spin(self, desired_frequency):

        t = time.time()
        self._s_frequency_queue.append(t)
        self._s_frequency = 10.0 / \
            (self._s_frequency_queue[-1] - self._s_frequency_queue[0])

        if not self._previous_spin:
            self._previous_spin = 0

        desired_time = 1.0 / desired_frequency
        time_diff = t - self._previous_spin
        time_wait = desired_time - time_diff

        if time_wait > 0:
            self._accumulated_spin += time_wait
        else:
            self._accumulated_spin = 0

        if self._accumulated_spin > 0.004:
            time.sleep(self._accumulated_spin)
            self._accumulated_spin = 0
            
        self._previous_spin = time.time()


