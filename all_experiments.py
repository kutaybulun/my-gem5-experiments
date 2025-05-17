"""
usage:
    to run all simulations:
        gem5riscv -re -m gem5.utils.multisim all_experiments.py
    to get the id of each simulation:
        gem5riscv all_experiments.py --list
    to run a specific simulation:
        gem5riscv all_experiments.py <id>
"""
import os
import sys

script_dir = os.path.abspath(os.path.dirname(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

from components import (
    RISCVBoard,
    PrivateL1SharedL2Cache,
    DDR4,
    InOrderCPU,
    OutOfOrderCPU,
)
from gem5.simulate.simulator import Simulator
from gem5.resources.resource import obtain_resource
from gem5.utils.multisim import multisim
from pathlib import Path

multisim.set_num_processes(8)

def get_board_inorder():
    cache = PrivateL1SharedL2Cache()
    memory = DDR4()
    cpu = InOrderCPU()

    board = RISCVBoard(
        clk_freq="1GHz", processor=cpu, cache_hierarchy=cache, memory=memory
    )

    return board

def get_board_o3(width, rob_size, num_int_regs, num_fp_regs, fetchB_size, fetchQ_size, instructionQ_size, loadQ_size, storeQ_size):
    cache = PrivateL1SharedL2Cache()
    memory = DDR4()
    cpu = OutOfOrderCPU(width, rob_size, num_int_regs, num_fp_regs, fetchB_size, fetchQ_size, instructionQ_size, loadQ_size, storeQ_size)

    board = RISCVBoard(
        clk_freq="1GHz", processor=cpu, cache_hierarchy=cache, memory=memory
    )

    return board

# In-order CPU configuration
board_inorder = get_board_inorder()
board_inorder.set_se_binary_workload(
    obtain_resource(resource_id="riscv-matrix-multiply")
)

# Out-of-order CPU configurations
configurations = {
    "little": {"width": 4, "rob_size": 32, "num_int_regs": 64, "num_fp_regs": 64, "fetchB_size": 4, "fetchQ_size": 8, "instructionQ_size": 16, "loadQ_size": 16, "storeQ_size": 16},
    "big": {"width": 12, "rob_size": 384, "num_int_regs": 512, "num_fp_regs": 512},
}
board_o3 = get_board_o3(**configurations["little"])
board_o3.set_se_binary_workload(
    obtain_resource(resource_id="riscv-matrix-multiply")
)

# Simulator Runs
simulator_inorder = Simulator(board=board_inorder, id="inorder-riscv-matrix-multiply")

simulator_o3 = Simulator(board=board_o3, id="o3-riscv-matrix-multiply")

multisim.add_simulator(simulator_inorder)
multisim.add_simulator(simulator_o3)