from matplotlib.pyplot import cla
import numpy as np
from .loop_filter import LoopFilter

# This get error from discriminator and calculate NCO command
# 'Euler' refers to backward Euler method to discritize transfer funtion
# 'Order2' means a order-2 lowpass filter is used 
# 'direct' here means no futher coherent or non-coherent integration is used 
class EulerOrder2Direct(LoopFilter):
    def __init__(self,bd,K,gap) -> None:
        super().__init__()
        self.noise_bandwidth = bd           # equivalent noise band width
        self.K = K                          # amplitude gain of the filter 
        self.error_pre = 0                  # the record of error
        self.NCO_pre = 0                    # the record of NCO command
        self.tau1 = 0                       # tau1 of the filter 
        self.tau2 = 0                       # tau2 of the filter
        self.gap_time = gap                 # time gap between two values, different from accumulation time 
        self.wn = 0                         # natural frequency of the filter 
        self.damping = 0.707                # damping ratio is set 0.707
        self.__cal_coefficient()            # calculate coefficient: wn, tau1 and tau2

    # Calcutate coefficient including wn, tau1 and tau2
    def __cal_coefficient(self):
        self.wn=self.noise_bandwidth/0.53
        self.tau1=self.K/(self.wn**2)
        self.tau2=2*self.damping/self.wn

    # set attribute including equivalent noise bandwidth, gain K and gap time
    # calling this function also automatically change the coeffcient of filter
    def set_attribute(self,bandwidth,K,gap):
        self.noise_bandwidth=bandwidth
        self.K=K
        self.gap_time=gap
        self.__cal_coefficient()

    def cal_NCO_command(self,error):
        NCO=self.NCO_pre+self.tau2/self.tau1*(error-self.error_pre)+error*(self.gap_time/self.tau1)
        self.NCO_pre=NCO
        self.error_pre=error
        return NCO
        pass
