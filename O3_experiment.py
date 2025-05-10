from components import (
    RISCVBoard,
    PrivateL1SharedL2Cache,
    DDR4,
    OutOfOrderCPU,
)
from gem5.simulate.simulator import Simulator
from gem5.resources.resource import obtain_resource

def get_board(width, rob_size, num_int_regs, num_fp_regs):
    cache = PrivateL1SharedL2Cache()
    memory = DDR4()
    cpu = OutOfOrderCPU(width, rob_size, num_int_regs, num_fp_regs)

    board = RISCVBoard(
        clk_freq="1GHz", processor=cpu, cache_hierarchy=cache, memory=memory
    )

    return board

configurations = {
    "little": {"width": 4, "rob_size": 32, "num_int_regs": 64, "num_fp_regs": 64},
    "big": {"width": 12, "rob_size": 384, "num_int_regs": 512, "num_fp_regs": 512},
}

board = get_board(**configurations["big"])
board.set_se_binary_workload(
    obtain_resource(resource_id="riscv-matrix-multiply")
)

simulator = Simulator(board=board, id="big-hello")
simulator.run()