from cmath import pi
from math import exp, floor
import queue
from random import sample
from source_processor.file_source_processor import FileSourceThread
import threading
import numpy as np
from queue import Queue
from channel.tracking.track_thread import TrackThread
import matplotlib.pyplot as plt

signal_buffer=Queue(maxsize=1e3)
fileReader=FileSourceThread(1,"filereader","e:/data/sig_codejam_40dB_0bitshift_1087freqshift_perHz.dat",'c8',signal_buffer,6e3*2e3)
init_state=np.array([0,1023e3,0,1e6])
res_buffer=Queue(1000)
track_thread=TrackThread(2,"tracker",6e6,signal_buffer,2,1023,init_state,res_buffer,2e3,4)

fileReader.start()
track_thread.start()

track_results=np.zeros([0,14])
count=0
while(True):
    try:
        track_res=res_buffer.get(timeout=10)
        count=count+1
        print("ms:%10d Ip:%10.3f, Ie:% 10.3f, Il:% 10.3f, Qp:% 10.3f ,codephase:%10.3f freq:%10.3f carrphase:%12.3f freq:%12.3f CN0:% 10.3f , SNR:%10.3f"%(count,track_res[0],track_res[1],track_res[2],track_res[3],track_res[6],track_res[7],track_res[8],track_res[9],track_res[10],track_res[13]))
        track_results=np.append(track_results,[track_res],axis=0)
    except:
        break

Ips=track_results[0:1000,0]
Ip_fft=np.fft.fft(Ips)
plt.figure(1)
plt.subplot(2,1,1)
plt.plot(np.abs(Ip_fft))
plt.subplot(2,1,2)
plt.plot(Ips)
plt.show()
