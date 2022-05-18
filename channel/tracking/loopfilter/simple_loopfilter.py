from .loop_filter import LoopFilter
class SimpleLoopFilter(LoopFilter):
    def __init__(self) -> None:
        super().__init__()
        pass

    def cal_NCO_command(self,error):
        return 0
        pass

    