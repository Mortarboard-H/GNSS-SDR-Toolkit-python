from cmath import pi
from math import exp, floor
from random import sample
from source_processor.file_source_processor import FileSourceThread
import threading
import numpy as np
from queue import Queue
from channel.tracking.track_thread import TrackThread
from public.cal_CA_code import generateCAcode

#generate simple signal
filename="test_signal_bitshift.dat"
fid=open(filename,'wb')
fid.close()
total_time=30               #30s
prn=2                       #prn 2
carrier_freq=1e3            #carrier frequency 1kHz
sample_rate=6e6             #sample frequency 6MHz
code=generateCAcode(prn)
chip_per_sample=1023e3/sample_rate
carrier_pahse_per_sample=carrier_freq*2*pi/sample_rate
for i in range(total_time): #s
    databit=-1
    fid=open(filename,'ab')
    for j in range(0,int(1e3)):  #ms
        if(j%20==0):
            databit=databit*-1
        cur_carrier_phase=np.linspace(0,1e-3,sample_rate/1e3,False)
        cur_carrier_phase=cur_carrier_phase*2*pi*carrier_freq
        cur_carrier_phase=cur_carrier_phase%(2*pi)

        cur_code_phase=np.linspace(0,1023,sample_rate/1e3,False)
        cur_chip_index=np.floor(cur_code_phase).astype('i4')
        cur_code=code[cur_chip_index]
        cur_sig=np.exp(1j*cur_carrier_phase)
        cur_sig=cur_sig*cur_code*databit
        noise_real=np.random.normal(0,0.5,len(cur_sig))
        noise_imag=np.random.normal(0,0.5,len(cur_sig))
        cur_sig=cur_sig+noise_real+1j*noise_imag
        cur_sig=cur_sig.astype('c8')
        
        np.ndarray.tofile(cur_sig,fid)
        
    print("finish sec:%d"%(i))
    fid.close()

            




# the place stores shared data
shared_data=Queue(1e4)




