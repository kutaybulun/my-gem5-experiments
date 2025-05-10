
from gem5.components.boards.simple_board import SimpleBoard
from gem5.components.cachehierarchies.classic.private_l1_shared_l2_cache_hierarchy \
    import PrivateL1SharedL2CacheHierarchy
from gem5.components.memory.dram_interfaces.ddr4 import DDR4_2400_8x8
from gem5.components.memory.memory import ChanneledMemory
from .processors import OutOfOrderCPU
from .processors import InOrderCPU

RISCVBoard = SimpleBoard

class PrivateL1SharedL2Cache(PrivateL1SharedL2CacheHierarchy):
    def __init__(self):
        super().__init__(
            l1i_size="32KiB",
            l1i_assoc=8,
            l1d_size="32KiB",
            l1d_assoc=8,
            l2_size="256KiB",
            l2_assoc=16,
        )

class DDR4(ChanneledMemory):
    """
    DDR4 models a 1 GiB single channel DDR4 DRAM memory with a data
    bus clocked at 2400MHz.

    The theoretical peak bandwidth of DDR4 is 19.2 GB/s.
    """
    def __init__(self):
        super().__init__(DDR4_2400_8x8, 1, 128, size="1GiB")

__all__ = [
    "RISCVBoard",
    "PrivateL1SharedL2Cache",
    "DDR4",
    "OutOfOrderCPU",
    "InOrderCPU",
]