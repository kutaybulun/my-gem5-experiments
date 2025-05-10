from components import (
    RISCVBoard,
    PrivateL1SharedL2Cache,
    DDR4,
    InOrderCPU,
)
from gem5.simulate.simulator import Simulator
from gem5.resources.resource import obtain_resource

def get_board():
    cache = PrivateL1SharedL2Cache()
    memory = DDR4()
    cpu = InOrderCPU()

    board = RISCVBoard(
        clk_freq="1GHz", processor=cpu, cache_hierarchy=cache, memory=memory
    )

    return board


board = get_board()
board.set_se_binary_workload(
    obtain_resource(resource_id="riscv-matrix-multiply")
)

simulator = Simulator(board=board, id="inorder-hello")
simulator.run()