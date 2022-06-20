from cmath import pi
from math import exp, floor
import queue
from random import sample
from source_processor.file_source_processor import FileSourceThread
import threading
import numpy as np
from queue import Queue
from channel.tracking.track_thread import TrackThread
from multiprocessing import  Process
import os

def test_accumulation(accu,filename,target_path):
    signal_buffer=Queue(maxsize=1e3)
    ms_to_process=4e3
    sample_num=ms_to_process*6e3
    fileReader=FileSourceThread(1,"filereader",filename,'c8',signal_buffer,sample_num)
    init_state=np.array([0,1023e3,0,1e6])
    res_buffer=Queue(1000)
    track_thread=TrackThread(2,"tracker",6e6,signal_buffer,2,1023,init_state,res_buffer,ms_to_process,accu)

    fileReader.start()
    track_thread.start()

    track_results=np.array([])
    count=0
    savefile=target_path+"/trackres_"+str(accu)+"ms.txt"
    fid=open(savefile,'w')
    print("start to track %d"%accu)
    info="%10s,%10s,%10s,%10s,%10s\n"%("CN0","SNR","time","code freq","carrier freq")
    fid.write(info)
    while(count<ms_to_process):
        try:
            track_res=res_buffer.get(timeout=10)
            count=count+1
            if(count%100==0 and count>0):
                print("accumulation for % 10d at time % 10d second, track res: CN0:% 10.3f , SNR:%10.3f"%(accu,count/1000,track_res[10],track_res[13]))
                info="%10.3f,%10.3f,%10.3f,%10.3f,%10.3f\n"%(track_res[10],track_res[13],count/1000,track_res[7],track_res[9])
                fid.write(info)
            np.append(track_results,track_res)
        except:
            break
    fid.close()
    fileReader.join()
    track_thread.join()
    print("end track %d"%accu)




# if __name__ == '__main__':
#     sourcepath="../data/"
#     for freq_shift in range(-2000,2050,50):                                         # different frequency shift in different folders
#         target_path="../data/freqshift_accumulation/freq_shift"+str(freq_shift)                                # put results in different folders
#         folder = os.path.exists(target_path)                                        # create the folder if not exist
#         if not folder:
#             os.makedirs(target_path)
#             print("make a path: %s"%(target_path))
#         else:
#             print("path: %s  already exists!"%(target_path))
#         sourcefile=sourcepath+"sig_codejam_40dB_0bitshift_"+str(freq_shift)+"freqshift.dat"  # the name of source file

#         print("start to test signal with %d frequency shift"%(freq_shift))
#         for j in range(1,101,8):                                                    # accumulation time, five process every time
#             process_list = []
#             for i in range(j,j+8):  #开启5个子进程执行fun1函数
#                 accu=i
#                 p = Process(target=test_accumulation,args=(accu,sourcefile,target_path,)) #实例化进程对象
#                 p.start()
#                 process_list.append(p)

#             for i in process_list:
#                 p.join()
#             print('end a loop')
#         print('结束测试')


# ## the main function used to power gain and accumulation effects on jamming mitigation
# if __name__ == '__main__':
#     sourcepath="../data/"
#     for power_gain in range(-20,50,1):                                         # different frequency shift in different folders
#         target_path="../data/dB_accumulation_rand/powerdB"+str(power_gain)                                # put results in different folders
#         folder = os.path.exists(target_path)                                        # create the folder if not exist
#         if not folder:
#             os.makedirs(target_path)
#             print("make a path: %s"%(target_path))
#         else:
#             print("path: %s  already exists!"%(target_path))
#         sourcefile=sourcepath+"sig_codejam_"+str(power_gain)+"dB_0bitshift_"+"0"+"freqshift.dat"  # the name of source file

#         print("start to test signal with %d dB power gain"%(power_gain))
#         for j in range(1,101,8):                                                    # accumulation time, five process every time
#             process_list = []
#             for i in range(j,j+8):  #开启5个子进程执行fun1函数
#                 accu=i
#                 p = Process(target=test_accumulation,args=(accu,sourcefile,target_path,)) #实例化进程对象
#                 p.start()
#                 process_list.append(p)

#             for i in process_list:
#                 p.join()
#             print('end a loop')
#         print('结束测试')


if __name__ == '__main__':
    sourcepath="e:/data/"
    for freq_shift in range(0,1000,200):                                         # different frequency shift in different folders
        target_path="e:/data/freqshift_filter_order/freq_shift"+str(freq_shift)                                # put results in different folders
        folder = os.path.exists(target_path)                                        # create the folder if not exist
        if not folder:
            os.makedirs(target_path)
            print("make a path: %s"%(target_path))
        else:
            print("path: %s  already exists!"%(target_path))
        sourcefile=sourcepath+"sig_codejam_40dB_0bitshift_"+str(freq_shift)+"freqshift_rand.dat"  # the name of source file

        print("start to test signal with %d frequency shift"%(freq_shift))
        for j in range(0,1):                                                    # accumulation time, five process every time
            process_list = []
            for i in range(j+6,j+27,2):  #开启5个子进程执行fun1函数
                accu=i
                p = Process(target=test_accumulation,args=(accu,sourcefile,target_path,)) #实例化进程对象
                p.start()
                process_list.append(p)

            for i in process_list:
                p.join()
            print('end a loop')
        print('结束测试')
