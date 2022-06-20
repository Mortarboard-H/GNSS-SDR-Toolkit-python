from cmath import exp, pi
from math import cos
import numpy as np
from .synchronizer import Synchronizer
class DirectSynchronizer(Synchronizer):

    def __init__(self,
                code_phase:float,
                code_frequency:float,
                carr_phase:float,
                carr_frequency:float,
                samprate:float,
                codelen:int,
                code:np.array) -> None:
        super().__init__(code_phase,code_frequency,carr_phase,carr_frequency,samprate,codelen,code)
        self.__init_code_phase=code_phase
        self.__init_code_frequency=code_frequency
        self.__init_carrier_phase=carr_phase
        self.__init_carrier_frequency=carr_frequency
        self.__sample_rate=samprate
        self.__code_length=codelen
        self.__spreading_code=code
        pass

    # set initial code phase for next round, should be called every time after a synchronizing
    def set_init_code_phase(self,codephase:float):
        self.__init_code_phase=codephase
        pass
    
    # set initial code frequency for next round, should be called every time after a synchronizing
    def set_init_code_freq(self,codefreq:float):
        self.__init_code_frequency=codefreq
        pass
    
    # set initial carrier phase for next round
    def set_init_carrier_phase(self,carrphase:float):
        self.__init_carrier_phase=carrphase
        pass

    #set initial carrier frequency for next round
    def set_init_carrier_frequency(self,carrfreq:float):
        self.__init_carrier_frequency=carrfreq
        pass

    #generate local code and carrier to dispatch them from signal
    def synchronizing(self,data:np.array):
        self.cur_code_phase=self.__init_code_phase
        self.cur_carrier_phase=self.__init_carrier_phase
        chip_per_sample=self.__init_code_frequency/self.__sample_rate
        carr_phase_per_sample=self.__init_carrier_frequency*2*pi/self.__sample_rate

        total_time=len(data)/self.__sample_rate
        t=np.linspace(0,total_time,len(data),False)

        carrier_phase=t*2*pi*self.__init_carrier_frequency+self.__init_carrier_phase
        carrier_phase=carrier_phase%(2*pi)

        code_phase=t*self.__init_code_frequency+self.__init_code_phase
        code_phase=code_phase%self.__code_length
        code_chip_index=np.floor(code_phase).astype('i4')
        code_chip=self.__spreading_code[code_chip_index]

        self.cur_carrier_phase=carrier_phase[-1]+carr_phase_per_sample
        self.cur_code_phase=code_phase[-1]+chip_per_sample

        local_sig=np.exp(-1j*carrier_phase)*code_chip
        data=local_sig*data
        return data

        pass

