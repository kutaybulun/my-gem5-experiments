"""
usage:
    to run all simulations:
        gem5riscv -re -m gem5.utils.multisim <script name>
    to get the id of each simulation:
        gem5riscv <script name> --list
    to run a specific simulation:
        gem5riscv <script name> <id>
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
from gem5.resources.resource import BinaryResource
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

# Binary path for a local resource
binary = BinaryResource(local_path="/home/kutaybulun/Repos/my-gem5-experiments/workloads/queens/queens")

# In-order CPU configuration
board_inorder = get_board_inorder()

board_inorder.set_se_binary_workload(
    binary,
    arguments=["16"]
)

simulator_inorder = Simulator(board=board_inorder, id="inorder-queens")
multisim.add_simulator(simulator_inorder)

# Out-of-order CPU configurations
# For sweeping the parameters we have a base configuration.
base= {
    "width": 4,
    "rob_size": 128,
    "num_int_regs": 128,
    "num_fp_regs": 128,
    "fetchB_size": 64,
    "fetchQ_size": 32,
    "instructionQ_size": 64,
    "loadQ_size": 128,
    "storeQ_size": 128,
}

very_big = {
    "width": 12,
    "rob_size": 512,
    "num_int_regs": 512,
    "num_fp_regs": 512,
    "fetchB_size": 64,
    "fetchQ_size": 512,
    "instructionQ_size": 512,
    "loadQ_size": 512,
    "storeQ_size": 512,
}

very_small = {
    "width": 4,
    "rob_size": 32,
    "num_int_regs": 64,
    "num_fp_regs": 64,
    "fetchB_size": 32,
    "fetchQ_size": 16,
    "instructionQ_size": 16,
    "loadQ_size": 32,
    "storeQ_size": 32,
}

sweeps = []

# Very big configuration
sweeps.append(("very-big", very_big))
sweeps.append(("base", base))
sweeps.append(("very-small", very_small))

# Sweep width
for w in [2, 4, 8, 10, 12]:
    cfg = base.copy()
    cfg["width"] = w
    sweeps.append(("width-%02d" % w, cfg))

# Sweep ROB size
for rob in [32, 64, 128, 256, 512]:
    cfg = base.copy()
    cfg["rob_size"] = rob
    sweeps.append(("rob-%03d" % rob, cfg))

# Sweep register file size
for regs in [32, 64, 128, 256, 512]:
    cfg = base.copy()
    cfg["num_int_regs"] = regs
    cfg["num_fp_regs"] = regs
    sweeps.append(("physical-regs-%03d" % regs, cfg))

# Sweep fetch queue size
for fetchQ in [32, 64, 128, 256, 512]:
    cfg = base.copy()
    cfg["fetchQ_size"] = fetchQ
    sweeps.append(("fetchQ-%02d" % fetchQ, cfg))

# Sweep instruction queue size
for instructionQ in [32, 64, 128, 256, 512]:
    cfg = base.copy()
    cfg["instructionQ_size"] = instructionQ
    sweeps.append(("instructionQ-%02d" % instructionQ, cfg))

# Sweep load queue and store queue size
for lsQ in [32, 64, 128, 256, 512]:
    cfg = base.copy()
    cfg["loadQ_size"] = lsQ
    cfg["storeQ_size"] = lsQ
    sweeps.append(("lsQ-%02d" % lsQ, cfg))

for name, params in sweeps:
    board_o3 = get_board_o3(**params)
    board_o3.set_se_binary_workload(
        binary,
        arguments=["16"]
    )
    sim_o3 = Simulator(
        board=board_o3,
        id=f"o3-{name}-queens",
    )
    multisim.add_simulator(sim_o3)

