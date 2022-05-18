from .discriminator import Discriminator
import numpy as np
class SimpleDiscriminator(Discriminator):
    def __init__(self) -> None:
        super().__init__()
        pass

    # direct return 0 for pll discriminator
    def discriminate_pll(self):
        return 0
        pass
    
    # direct return 0 for dll discriminator
    def discirminate_dll(self):
        return 0
        pass