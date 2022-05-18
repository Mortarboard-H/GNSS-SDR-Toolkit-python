import numpy as np
from .lock_detector import LockDetector
class VSMDetector(LockDetector):
    def __init__(self,amount,accu) -> None:
        super().__init__()
        self.accu_time=accu     #the accumulation time, in seconds
        self.K=amount           #the amount of samples
        self.CN0=0              #CN0
        self.meanZ=0            #mean of z
        self.varZ=0             #variance of z
        self.indexZ=0           #the empty place of z
        self.Z=np.zeros(self.K,)     #a container for z
        self.SNR=0              # signal to noise ratio
        pass

    def cal_CN0(self,Ip:float,Qp:float):
        self.Z[self.indexZ]=(Ip**2+Qp**2)
        valid=self.Z!=0
        self.indexZ=self.indexZ+1
        self.indexZ=self.indexZ%self.K
        self.CN0=0
        self.varZ=np.var(self.Z[valid])
        self.meanZ=np.mean(self.Z[valid])
        Ps=np.sqrt(self.meanZ*self.meanZ-self.varZ)
        Pn=self.meanZ-Ps
        if(Pn!=0):
            self.CN0=10*np.log10(Ps/Pn/self.accu_time)
            self.SNR=10*np.log10(Ps/Pn)
        return self.CN0

        
