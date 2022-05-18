# The interface of discriminator, a discriminator must provide a code phase discriminator
# and a carrier phase disciminator
# and the amplitute gain of the discrminator must be 1
class Discriminator:
    def __init__(self) -> None:
        pass

    def discriminator_pll(self,Ip,Ie,Il,Qp,Qe,Ql):
        pass

    def discriminator_dll(self,Ip,Ie,Il,Qp,Qe,Ql):
        pass