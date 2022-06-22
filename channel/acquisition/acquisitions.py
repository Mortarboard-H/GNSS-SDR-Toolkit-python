from threading import local
import numpy as np
from queue import Queue
from public.cal_CA_code import generateCAcode


def  cal_correlation(sequence1,sequence2):
    s1_freq=np.fft.fft(sequence1)           #calculate the frequency domain of sequency1
    s2_freq=np.fft.fft(sequence2)           # calculate the frequency domain of sequence2
    s2_freq=np.conj(s2_freq)                # calculate the conj
    corr=np.abs(np.fft.ifft(s1_freq*s2_freq))   # calculate correlation
    return corr


# a father class for all GPS_L1_acquisition methods
# Defines the variables to be used in all methods
class GPS_L1_Acquisition:
    def __init__(self,sample_rate:int,
                    source_buffer:Queue,
                    prn:int,
                    code_length:int,
                    center_freq,
                    freq_search_range
                    ) -> None:
        self.sample_rate=sample_rate
        self.source_buffer=source_buffer
        self.prn=prn
        self.code=generateCAcode(self.prn)
        self.code_length=code_length
        self.center_freq=center_freq
        self.freq_search_range=freq_search_range
        self.results={'isAcquired':False,'codePhse':0,'carrierFrequency':0,'metric':0}      # used to store the results of acquisition
        pass


# The implementation of a GPS L1 acquisition method
# frequency&code mat is calculated using PCPA method
# only 1ms of data is used in this method 
class GPS_L1_1ms_PCPA(GPS_L1_Acquisition):
    def __init__(self, sample_rate: int, source_buffer: Queue, prn: int, code_length: int,center_freq,freq_search_range) -> None:
        super().__init__(sample_rate, source_buffer, prn, code_length,center_freq,freq_search_range)
        self.freq_interval=50                                                               # interval of frequency in frequency and code phase mat
        self.freq_bin_Num=int(2*(self.freq_search_range/self.freq_interval))+1              # number of frequency bins
        self.code_bin_Num=int(self.sample_rate/1e3)                                         # number of code bins
        self.freq_code_mat=np.zeros(shape=[self.freq_bin_Num,self.code_bin_Num])            # frequency and code bins mat

    def process(self):
        freq_bin_index=0                                                                    # index of frequency bin
        origin_sig=np.zeros(self.code_bin_Num,)                                             # used to contain the original signal 
        is_enough=True                                                                      # 
        for i in range(0,self.code_bin_Num):
            try:
                origin_sig[i]=self.sourcebuffer.get(timeout=3)
            except:
                is_enough=False
                break
        if(not is_enough):
            print("unable to read enough data in acquisition")
            return self.results

        t=np.linspace(0,0.001,self.code_bin_Num,endpoint=False)
        local_code_phase=t*1.023e6
        local_code_phase=local_code_phase%self.code_length
        code_chip_index=np.floor(local_code_phase).astype('i4')
        code_chip=self.code[code_chip_index]                                                # The local code sequence
        for freq_bin in range(self.center_freq-self.freq_search_range,self.center_freq+self.freq_search_range+self.freq_interval,self.freq_interval):
            local_carrier=np.exp(-2*np.pi*freq_bin*t)                                       # generate local carrier signal
            temp_sig=origin_sig*local_carrier                                               # try to remove carrier frequency
            correlation=cal_correlation(temp_sig,code_chip)                                 # calculate correlation
            self.freq_code_mat[freq_bin_index]=correlation                                  # save correlation results
            freq_bin_index=freq_bin_index+1

        # find the peak in frequency and code mat
        max_value=np.max(self.freq_code_mat)
        max_freq,max_code=np.where(self.freq_code_mat==max_value)
        max_freq=max_freq[0]
        max_code=max_code[0]
        # record the initial estimiation
        if(max_value>np.mean(self.freq_code_mat)):
            self.results['isAcquired']=True
            self.results['codePhse']=max_code/self.code_bin_Num
            self.results['carrierFrequency']=max_freq*self.freq_interval+self.center_freq-self.freq_search_range
            self.results['metric']=max_value/(np.mean(self.freq_code_mat))
        
        return self.results
