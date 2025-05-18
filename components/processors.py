from gem5.isas import ISA
from gem5.components.processors.base_cpu_core import BaseCPUCore
from gem5.components.processors.base_cpu_processor import BaseCPUProcessor

from m5.objects import RiscvO3CPU
from m5.objects import RiscvMinorCPU
from m5.objects.FuncUnitConfig import *
from m5.objects.BranchPredictor import (
    TournamentBP,
)


class OutOfOrderCPUCore(RiscvO3CPU):
    def __init__(self, 
                 width, 
                 rob_size, 
                 num_int_regs, 
                 num_fp_regs,
                 fetchB_size,
                 fetchQ_size,
                 instructionQ_size,
                 loadQ_size,
                 storeQ_size):
        """
        OutOfOrderCPUCore extends RiscvO3CPU. RiscvO3CPU is one of gem5's
        internal models the implements an out of order pipeline.

        This class sets the width of the fetch, decode, rename, issue,
        writeback, and commit stages of the pipeline. It also sets the number
        of entries in the reorder buffer, the number of physical integer
        registers, and the number of physical floating point registers.

        There are many other parameters for the O3 CPU model, but we are only
        interested in the ones mentioned above.

        :param width: sets the width of fetch, decode, raname, issue, wb, and
        commit stages.
        :param rob_size: determine the number of entries in the reorder buffer.
        :param num_int_regs: determines the size of the integer register file.
        :param num_int_regs: determines the size of the vector/floating point
        register file.
        """
        super().__init__()
        # Width of the pipeline stages, max is 12
        self.fetchWidth = width
        self.decodeWidth = width
        self.renameWidth = width
        self.dispatchWidth = width
        self.issueWidth = width
        self.wbWidth = width
        self.commitWidth = width
        
        # Number of physical registers
        self.numPhysIntRegs = num_int_regs
        self.numPhysFloatRegs = num_fp_regs

        # Branch predictor
        self.branchPred = TournamentBP()

        # Queue sizes and buffer sizes
        self.fetchBufferSize = fetchB_size # default is 64B, shouldn't be biger than cache block size
        self.fetchQueueSize = fetchQ_size   # default is 32
        self.numIQEntries = instructionQ_size # default is 64
        self.LQEntries = loadQ_size # default is 32
        self.SQEntries = storeQ_size # default is 32

        # Reorder buffer size
        self.numROBEntries = rob_size


class OutOfOrderCPUStdCore(BaseCPUCore):
    def __init__(self, 
                 width, 
                 rob_size, 
                 num_int_regs, 
                 num_fp_regs,
                 fetchB_size,
                 fetchQ_size,
                 instructionQ_size,
                 loadQ_size,
                 storeQ_size):
        """
        OutOfOrderCPUStdCore wraps OutOfOrderCPUCore into a gem5 standard
        library core.

        :param width: sets the width of fetch, decode, raname, issue, wb, and
        commit stages.
        :param rob_size: determine the number of entries in the reorder buffer.
        :param num_int_regs: determines the size of the integer register file.
        :param num_int_regs: determines the size of the vector/floating point
        register file.
        """
        core = OutOfOrderCPUCore(width, 
                                 rob_size, 
                                 num_int_regs, 
                                 num_fp_regs, 
                                 fetchB_size, 
                                 fetchQ_size, 
                                 instructionQ_size, 
                                 loadQ_size, 
                                 storeQ_size)
        
        super().__init__(core, ISA.RISCV)


class OutOfOrderCPU(BaseCPUProcessor):
    def __init__(self, 
                 width, 
                 rob_size, 
                 num_int_regs, 
                 num_fp_regs,
                 fetchB_size,
                 fetchQ_size,
                 instructionQ_size,
                 loadQ_size,
                 storeQ_size):
        """
        OutOfOrderCPU models a single core CPU with support for the RISC-V
        instruction set architecture (ISA). This model uses the O3 CPU model
        which is an out of order pipelined CPU.

        Some parameters of the O3 CPU model are set in this class. Please refer
        to the OutOfOrderCPUCore class for more information.

        :param width: sets the width of fetch, decode, raname, issue, wb, and
        commit stages.
        :param rob_size: determine the number of entries in the reorder buffer.
        :param num_int_regs: determines the size of the integer register file.
        :param num_int_regs: determines the size of the vector/floating point
        register file.
        """
        cores = [
            OutOfOrderCPUStdCore(width, rob_size, num_int_regs, num_fp_regs, fetchB_size, fetchQ_size, instructionQ_size, loadQ_size, storeQ_size)
        ]
        super().__init__(cores)
        self._width = width
        self._rob_size = rob_size
        self._num_int_regs = num_int_regs
        self._num_fp_regs = num_fp_regs
        self._fetchB_size = fetchB_size
        self._fetchQ_size = fetchQ_size
        self._instructionQ_size = instructionQ_size
        self._loadQ_size = loadQ_size
        self._storeQ_size = storeQ_size

    def get_area_score(self):
        """
        get_area_score calculates the area score of a pipeline using its
        parameters width, rob_size, num_int_regs, and num_fp_regs.

        **IMPORTANT**: This is not a real area model.

        :return: the area score of a pipeline using its parameters width,
        rob_size, num_int_regs, and num_fp_regs.
        """
        score = (
            self._width * (2 * self._rob_size + self._num_int_regs + self._num_fp_regs)
            + 4 * self._width
            + 2 * self._rob_size
            + self._num_int_regs
            + self._num_fp_regs
        )
        return score

class InOrderCPUCore(RiscvMinorCPU):
    def __init__(self):
        super().__init__()
        # Only changes the branch predictor others are default for in-order
        self.branchPred = TournamentBP()

class InOrderCPUStdCore(BaseCPUCore):
    def __init__(self):
        core = InOrderCPUCore()
        super().__init__(core, ISA.RISCV)

class InOrderCPU(BaseCPUProcessor):
    def __init__(self):
        core = [
            InOrderCPUStdCore()
        ]
        super().__init__(core)