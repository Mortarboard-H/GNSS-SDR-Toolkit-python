from .track import *
from threading import Thread
from queue import Queue
import numpy as np
class TrackThread(Thread):
    def __init__(self,thread_id:int,
                thread_name,
                sample_rate:float,              #sample rate
                source_buffer:Queue,            #where to retrive signal data
                prn:int,                        #prn of the signal
                code_len:int,                   #length of CA code
                init_state:np.array,            #the initial code phase & frequency, carrier phase & frequency
                res_buffer:Queue,               #to store the result of tracking, incluing Ip Ie Il, Qp Qe Ql, code phase, code freq, carrier phase, carrier freq, 3 CN0, 1 SNR
                ms_to_process=1e10,             #length to process
                accu_time_ms=1                    #accumulation period, round of code
                ):
        Thread.__init__(self)
        self.thread_name=thread_name
        self.thread_id=thread_id
        self.__prn=prn
        #the size of initial state should be 4, including initial code phase& freq, carrier phase & freq
        assert len(init_state)==4, "Error! Length of initial state shoud be 4!"
        self.__tracker=TrackPerMs_NoBit_FiltOrder(sample_rate,source_buffer,prn,code_len,init_state,res_buffer,ms_to_process,accu_time_ms)

    def set_init_state(self,init_state):
        assert len(init_state)==4, "Error! Length of initial state shoud be 4!"
        self.__tracker.set_init_state(init_state[0],init_state[1],init_state[2],init_state[3])

    def run(self) -> None:
        print("start to track prn:%d \n"%(self.__prn))
        self.__tracker.tracking_process()
        print("stop tracking for prn:%d"%(self.__prn))