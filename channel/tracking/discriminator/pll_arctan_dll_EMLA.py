import numpy as np
from .discriminator import Discriminator
#This is an implemention of discriminator for carrier and code loop.
# phase error of carrier is calculated by arctan(Qp/IP)
# phase error of code loop is calculated by early-minus-late amplitude (EMLA) algorithm
class ArctanCarrierEMLACode(Discriminator):
    def __init__(self) -> None:
        super().__init__()
        pass

    # calculate carrier phase error by actan(Qp/Ip)
    def discriminator_pll(self,Ip,Ie,Il,Qp,Qe,Ql):
        return np.arctan(Qp/Ip)
        pass
    
    # calculate code loop error by EMLA 
    def discriminator_dll(self,Ip,Ie,Il,Qp,Qe,Ql):
        return (np.sqrt(Ie**2+Qe**2)-np.sqrt(Il**2+Ql**2))/(np.sqrt(Ie**2+Qe**2)+np.sqrt(Il**2+Ql**2))
        pass
