#!/usr/bin/env python3
from pathlib import Path

# 1) Standard-library board and components
from gem5.components.boards.simple_board import SimpleBoard
from gem5.components.cachehierarchies.classic.private_l1_shared_l2_cache_hierarchy \
    import PrivateL1SharedL2CacheHierarchy
from gem5.components.memory.single_channel import SingleChannelDDR4_2400
from gem5.components.processors.simple_processor import SimpleProcessor
from gem5.components.processors.cpu_types import CPUTypes
from gem5.isas import ISA
from gem5.resources.resource import obtain_resource

# 2) SE-mode workload helper
from gem5.components.boards.se_binary_workload import SEBinaryWorkload

# 3) Top-level simulation driver
from gem5.simulate.simulator import Simulator

# 1) Build a 2 GHz board with private L1 + shared L2
cache_hierarchy = PrivateL1SharedL2CacheHierarchy(
    l1d_size="32kB", l1i_size="32kB", l2_size="256kB"
)
memory = SingleChannelDDR4_2400(size="2GiB")
processor = SimpleProcessor(cpu_type=CPUTypes.TIMING, num_cores=1, isa=ISA.RISCV)

board = SimpleBoard(
    clk_freq="2GHz",
    processor=processor,
    memory=memory,
    cache_hierarchy=cache_hierarchy,
)

# 2) Point to your local RISC-V “hello” binary
#hello_bin = Path("/home/kutay-ozu-u-22045/Tools/gem5/tests/test-progs/hello/bin/riscv/linux/hello")

# 3) Install the workload on the board
board.set_se_binary_workload(
    obtain_resource("riscv-hello", resource_version="1.0.0")
)

# 4) Run the simulation!
sim = Simulator(board=board)
sim.run()
