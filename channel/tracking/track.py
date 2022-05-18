from queue import Queue
from wsgiref.util import shift_path_info


import numpy as np
#from discriminator.simple_discriminator import SimpleDiscriminator
#from .discriminator.simple_discriminator import SimpleDiscriminator
from .discriminator.pll_arctan_dll_EMLA import ArctanCarrierEMLACode
from .synchronizer.synchronizer import Synchronizer
from .synchronizer.direct_synchronizer import DirectSynchronizer
from .loopfilter.loop_filter import LoopFilter
from .loopfilter.simple_loopfilter import SimpleLoopFilter
from .loopfilter.euler_order2_direct import EulerOrder2Direct
from .lockdetector.lock_detector import LockDetector
from .lockdetector.VSM import VSMDetector

from sys import path
path.append("..")

from public.cal_CA_code import generateCAcode


# Father class for all trackings. This class mainly deal with the shared function of all tracking methods
class Tracking:
    def __init__(self,
                    sampRate:float,
                    sourcebuffer:Queue,
                    prn:int,
                    codelen:int,
                    initstate:np.array,             #storing initial code phase & frequency, carrier phase & frequency
                    res_buffer:Queue,               # A shared queue providing results of tracking for next procedure
                    ms_to_process=1e10,             #length to process
                    accu_time_ms=1                    #accumulation period, round of code
                    ) -> None:
        self.sourcebuffer=sourcebuffer
        self.prn=prn
        self.ms_to_process=ms_to_process
        self.sample_rate=sampRate
        self.code_length=codelen
        self.accu_time=accu_time_ms
        self.init_code_phase=initstate[0]
        self.init_code_frequency=initstate[1]
        self.init_carrier_phase=initstate[2]
        self.init_carrier_frequency=initstate[3]
        self.code=generateCAcode(prn)
        self.res_buffer=res_buffer
        self.final_res = np.zeros(14,)                            # The final result to be transferred. 
                                                                    # Index 0-5 are for Ip, Ie, Il, Qp, Qe, Ql, 
                                                                    # Index 6-9 are for code phase, code frequency, carrier phase, carrier frequency
                                                                    # Index 10-12 are for carrier to noise ratio
                                                                    # Index 13 is the signal to noise ratio

    # set initial state: initial code phase&frequency,initial carrier phase& frequency
    def set_init_state(self,init_code_phase,init_code_frequency,init_carrier_phase,init_carrier_freq): 
        self.init_code_phase=init_code_phase
        self.init_code_frequency=init_code_frequency
        self.init_carrier_phase=init_carrier_phase
        self.init_carrier_frequency=init_carrier_freq

# A simple implemention of tracking algorithms.
# This method produces results every accumulation time, which means the larger the accumulation time
# The slower it generates final results 
class Trackor(Tracking):
    def __init__(self,
                    sampRate:float,
                    sourcebuffer:Queue,
                    prn:int,
                    codelen:int,
                    initstate:np.array,             #storing initial code phase & frequency, carrier phase & frequency
                    res_buffer:Queue,               # A shared queue providing results of tracking for next procedure
                    ms_to_process=1e10,             #length to process
                    accu_time_ms=1                    #accumulation period, round of code
                    ) -> None:
        
        super().__init__(sampRate,sourcebuffer,prn,codelen,initstate,res_buffer,ms_to_process,accu_time_ms)
        self.synchronizer=DirectSynchronizer(self.init_code_phase,self.init_code_frequency,self.init_carrier_phase,self.init_carrier_frequency,self.sample_rate,self.code_length,self.code)
        self.discriminator=ArctanCarrierEMLACode()
        self.lockdetector=VSMDetector(200,self.accu_time/1e3)
        self.phase_loopfilter=EulerOrder2Direct(5,1,self.accu_time/1e3)
        self.code_loopfilter=EulerOrder2Direct(5,1,self.accu_time/1e3)
        pass

    def tracking_process(self):
        cur_code_phase=self.init_code_phase
        cur_code_freq=self.init_code_frequency
        cur_carrier_phase=self.init_carrier_phase
        cur_carrier_freq=self.init_carrier_frequency
        processed_time=0
        while(processed_time<=self.ms_to_process):
            #calculate how many samples should be read
            chip_per_sample=cur_code_freq/self.sample_rate
            chip_to_process=0
            if(cur_code_phase<self.code_length/2):
                chip_to_process=self.accu_time*self.code_length-cur_code_phase
            else:
                chip_to_process=(self.accu_time+1)*self.code_length-cur_code_phase
            samples_to_process=chip_to_process/chip_per_sample
            samples_to_process=int(samples_to_process)
            
            #update processed time
            processed_time=processed_time+samples_to_process/self.sample_rate*1e3
            
            #create a buffer to store the samples to be processed
            data_buffer=np.zeros(int(samples_to_process),)
            data_buffer=data_buffer+0j
            is_enough=True
            for i in range(0,samples_to_process):
                try:
                    data_buffer[i]=self.sourcebuffer.get(timeout=3)
                except:
                    is_enough=False
                    break
            
            #stop the tracking process if not enough data read
            if(is_enough==False):
                print("Unable to get enough data! It seems that we reached the end of file!")
                break

            early_data=data_buffer.copy()
            late_data=data_buffer.copy()
            late_code_phase=cur_code_phase-0.5
            if(late_code_phase<0):
                late_code_phase=late_code_phase+self.code_length
            early_code_phase=cur_code_phase+0.5
            if(early_code_phase>=self.code_length):
                early_code_phase=early_code_phase-self.code_length
            #set the initial state of synchronizer and get prompt data
            self.synchronizer.set_init_carrier_frequency(cur_carrier_freq)
            self.synchronizer.set_init_carrier_phase(cur_carrier_phase)
            self.synchronizer.set_init_code_phase(cur_code_phase)
            self.synchronizer.set_init_code_freq(cur_code_freq)
            #generate local signal and synchronize with input data 
            data_buffer=self.synchronizer.synchronizing(data_buffer)

            cur_code_phase=self.synchronizer.cur_code_phase
            cur_carrier_phase=self.synchronizer.cur_carrier_phase

            p_data=np.sum(data_buffer)
            Ip=p_data.real
            Qp=p_data.imag

            #set state of the synchronizer and get early data
            
            self.synchronizer.set_init_code_phase(early_code_phase)
            early_data=self.synchronizer.synchronizing(early_data)

            e_data=np.sum(early_data)
            Ie=e_data.real
            Qe=e_data.imag

            #set state of the synchronizer and get late data
            self.synchronizer.set_init_code_phase(late_code_phase)
            late_data=self.synchronizer.synchronizing(late_data)

            l_data=np.sum(late_data)
            Il=l_data.real
            Ql=l_data.imag

            
            code_phase_error=self.discriminator.discriminator_dll(Ip,Ie,Il,Qp,Qe,Ql)
            carrier_phase_error=self.discriminator.discriminator_pll(Ip,Ie,Il,Qp,Qe,Ql)

            NCO_command_pll=self.phase_loopfilter.cal_NCO_command(carrier_phase_error)
            NCO_command_dll=self.code_loopfilter.cal_NCO_command(code_phase_error)

            cur_carrier_freq=self.init_carrier_frequency+NCO_command_pll
            cur_code_freq=self.init_code_frequency+NCO_command_dll

            CN0_VSM=self.lockdetector.cal_CN0(Ip,Qp)
            SNR=self.lockdetector.SNR

            self.final_res[0:6]=[Ip,Ie,Il,Qp,Qe,Ql]
            self.final_res[6:10]=[cur_code_phase,cur_code_freq,cur_carrier_phase,cur_carrier_freq]
            self.final_res[10]=CN0_VSM
            self.final_res[13]=SNR
            

            self.res_buffer.put(self.final_res.copy())
        
        self.init_carrier_frequency=cur_carrier_freq
        self.init_carrier_phase=cur_carrier_phase
        self.init_code_frequency=cur_code_freq
        self.init_code_phase=cur_code_phase

        pass
            


# A tracking method generate an output every ms
# No matter what the accumulation time is, this tracking method generates an output every ms. 
# It is done by using a container to store the tracking result of every ms and sum up them to 
# meet the requirement of accumulation time
class TrackPerMs(Tracking):
    def __init__(self,
                    sampRate:float,
                    sourcebuffer:Queue,
                    prn:int,
                    codelen:int,
                    initstate:np.array,             #storing initial code phase & frequency, carrier phase & frequency
                    res_buffer:Queue,               # A shared queue providing results of tracking for next procedure
                    ms_to_process=1e10,             #length to process
                    accu_time_ms=1                    #accumulation period, round of code
                    ) -> None:
        super().__init__(sampRate,sourcebuffer,prn,codelen,initstate,res_buffer,ms_to_process,accu_time_ms)
        self.__track_loop_times=int(self.accu_time)               # The round of 1 ms loop needed to meet the requirement of accumulation time
        self.__track_results = np.zeros([self.__track_loop_times,6])   # The container stores the direct tracking results of early rounds
        self._accu_time_pre_round=1         #1 ms
        # define the sychronizer to be used
        self.synchronizer=DirectSynchronizer(self.init_code_phase,self.init_code_frequency,self.init_carrier_phase,self.init_carrier_frequency,self.sample_rate,self.code_length,self.code)
        # define the discriminator to be used 
        self.discriminator=ArctanCarrierEMLACode()
        # define the lockdetector to be used
        self.lockdetector=VSMDetector(200,self.accu_time/1e3)
        # define the loop filter of carrier phase to be used. Note that T in transfer funciton refers to the gap between two inputs
        self.phase_loopfilter=EulerOrder2Direct(15,1,self._accu_time_pre_round/1e3)
        # define the loop filter of code phase to be used
        self.code_loopfilter=EulerOrder2Direct(15,1,self._accu_time_pre_round/1e3)
        
        pass
    
    # set initial state: initial code phase&frequency,initial carrier phase& frequency
    def set_init_state(self,init_code_phase,init_code_frequency,init_carrier_phase,init_carrier_freq): 
        super().set_init_state(init_code_phase,init_code_frequency,init_carrier_phase,init_carrier_freq)
        self.__track_results = np.zeros(self.__track_loop_times,)

    def tracking_process(self):
        cur_code_phase=self.init_code_phase
        cur_code_freq=self.init_code_frequency
        cur_carrier_phase=self.init_carrier_phase
        cur_carrier_freq=self.init_carrier_frequency
        processed_time=0
        while(processed_time<=self.ms_to_process):
            #calculate how many samples should be read
            chip_per_sample=cur_code_freq/self.sample_rate
            chip_to_process=0
            if(cur_code_phase<self.code_length/2):
                chip_to_process=self._accu_time_pre_round*self.code_length-cur_code_phase
            else:
                chip_to_process=(self._accu_time_pre_round+1)*self.code_length-cur_code_phase
            samples_to_process=chip_to_process/chip_per_sample
            samples_to_process=int(samples_to_process)
            
            #update processed time
            processed_time=processed_time+samples_to_process/self.sample_rate*1e3
            
            #create a buffer to store the samples to be processed
            data_buffer=np.zeros(int(samples_to_process),)
            data_buffer=data_buffer+0j
            is_enough=True
            for i in range(0,samples_to_process):
                try:
                    data_buffer[i]=self.sourcebuffer.get(timeout=3)
                except:
                    is_enough=False
                    break
            
            #stop the tracking process if not enough data read
            if(is_enough==False):
                print("Unable to get enough data! It seems that we reached the end of file!")
                break

            # copy data to calculte early phase and late phase results
            early_data=data_buffer.copy()
            late_data=data_buffer.copy()

            # calculate late code phase 
            late_code_phase=cur_code_phase-0.5
            if(late_code_phase<0):
                late_code_phase=late_code_phase+self.code_length
            # calculate early code phase
            early_code_phase=cur_code_phase+0.5
            if(early_code_phase>=self.code_length):
                early_code_phase=early_code_phase-self.code_length
            #set the initial state of synchronizer and get prompt data
            self.synchronizer.set_init_carrier_frequency(cur_carrier_freq)
            self.synchronizer.set_init_carrier_phase(cur_carrier_phase)
            self.synchronizer.set_init_code_phase(cur_code_phase)
            self.synchronizer.set_init_code_freq(cur_code_freq)
            #generate local signal and synchronize with input data 
            data_buffer=self.synchronizer.synchronizing(data_buffer)

            # update code phase and carrie phase for next sample 
            cur_code_phase=self.synchronizer.cur_code_phase
            cur_carrier_phase=self.synchronizer.cur_carrier_phase

            # calculate prompt result
            p_data=np.sum(data_buffer)
            Ip=p_data.real
            Qp=p_data.imag

            #set state of the synchronizer and get early data
            self.synchronizer.set_init_code_phase(early_code_phase)
            #generate local signal and synchronize with input data 
            early_data=self.synchronizer.synchronizing(early_data)

            e_data=np.sum(early_data)
            Ie=e_data.real
            Qe=e_data.imag

            #set state of the synchronizer and get late data
            self.synchronizer.set_init_code_phase(late_code_phase)
            #generate local signal and synchronize with input data 
            late_data=self.synchronizer.synchronizing(late_data)

            l_data=np.sum(late_data)
            Il=l_data.real
            Ql=l_data.imag

            # record direct tracking results and eliminate data bit
            res_round=np.zeros(6,)
            if(Ip<0):
                res_round[:]=[-Ip,-Ie,-Il,-Qp,-Qe,-Ql]
            else:
                res_round[:]=[Ip,Ie,Il,Qp,Qe,Ql]

            #update __track_results
            self.__track_results=np.roll(self.__track_results,1,0)
            self.__track_results[0]=res_round

            # calculate mean tracking results
            res_mean=np.sum(self.__track_results,0)
            
            #calculate code phase error and carrier phase error
            code_phase_error=self.discriminator.discriminator_dll(res_mean[0],res_mean[1],res_mean[2],res_mean[3],res_mean[4],res_mean[5])
            carrier_phase_error=self.discriminator.discriminator_pll(res_mean[0],res_mean[1],res_mean[2],res_mean[3],res_mean[4],res_mean[5])

            # calculate NCO command for pll and dll
            NCO_command_pll=self.phase_loopfilter.cal_NCO_command(carrier_phase_error)
            NCO_command_dll=self.code_loopfilter.cal_NCO_command(code_phase_error)

            # update carrier frequency and code frequency
            cur_carrier_freq=self.init_carrier_frequency+NCO_command_pll
            cur_code_freq=self.init_code_frequency+NCO_command_dll

            # calculate VSM carrier to noise ratio
            CN0_VSM=self.lockdetector.cal_CN0(Ip,Qp)
            SNR=self.lockdetector.SNR

            if(Ip<0):  
                self.final_res[0:6]=[-res_mean[0],-res_mean[1],-res_mean[2],-res_mean[3],-res_mean[4],-res_mean[5]]
            else:
                self.final_res[0:6]=[res_mean[0],res_mean[1],res_mean[2],res_mean[3],res_mean[4],res_mean[5]]
            self.final_res[6:10]=[cur_code_phase,cur_code_freq,cur_carrier_phase,cur_carrier_freq]
            self.final_res[10]=CN0_VSM
            self.final_res[13]=SNR

            self.res_buffer.put(self.final_res.copy())
        
        self.init_carrier_frequency=cur_carrier_freq
        self.init_carrier_phase=cur_carrier_phase
        self.init_code_frequency=cur_code_freq
        self.init_code_phase=cur_code_phase

        pass
            

    