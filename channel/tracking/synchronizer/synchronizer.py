import numpy as np
class Synchronizer:
    def __init__(self,
                code_phase:float,
                code_frequency:float,
                carr_phase:float,
                carr_frequency:float,
                samprate:float,
                codelen:int,
                code:np.array) -> None:
        super().__init__()
        self.__init_code_phase=code_phase
        self.__init_code_frequency=code_frequency
        self.__init_carrier_phase=carr_phase
        self.__init_carrier_frequency=carr_frequency
        self.__sample_rate=samprate
        self.__code_length=codelen
        self.__spreading_code=code
        self.cur_code_phase=code_phase
        self.cur_code_frequency=code_frequency
        self.cur_carrier_phase=carr_phase
        self.cur_carrier_frequency=carr_frequency
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

    def synchronizing(self,data:np.array):
        pass
