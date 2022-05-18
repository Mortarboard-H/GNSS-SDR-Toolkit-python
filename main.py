from cmath import pi
from math import exp, floor
import queue
from random import sample
from source_processor.file_source_processor import FileSourceThread
import threading
import numpy as np
from queue import Queue
from channel.tracking.track_thread import TrackThread

signal_buffer=Queue(maxsize=1e3)
fileReader=FileSourceThread(1,"filereader","test_signal_bitshift.dat",'c8',signal_buffer)
init_state=np.array([0,1023e3,0,1e3])
res_buffer=Queue(1000)
track_thread=TrackThread(2,"tracker",6e6,signal_buffer,2,1023,init_state,res_buffer,20e3,5)

fileReader.start()
track_thread.start()

track_results=np.array([])
while(True):
    try:
        track_res=res_buffer.get(timeout=10)
        print("track res: Ip:% 10.3f, Ie: % 10.3f, Il: % 10.3f, Qp: % 10.3f , Qe: % 10.3f, Ql: % 10.3f, CN0:% 10.3f "%(track_res[0],track_res[1],track_res[2],track_res[3],track_res[4],track_res[5],track_res[6]))
        np.append(track_results,track_res)
    except:
        break
