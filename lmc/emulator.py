import parser
from utils import (
    Instruction, instr_handler, registered_handlers
)


class LMCEmulator:
    # TODO: make a method for raising very detailed errors.
    def __init__(self, memory=None, prog_ctr=0, accumulator=0):
        if memory is None:
            memory = [0] * 100

        if len(memory) > 100:
            raise ValueError("Invalid memory size: " + str(len(memory)))

        while len(memory) < 100:
            memory.append(000)

        self.memory = memory
        self.prog_ctr = prog_ctr
        self.accumulator = accumulator
        self.running = False

        self.output = ""

    def main_loop(self):
        self.running = True
        while self.running:
            value = self.memory[self.prog_ctr]
            padded = str(value).zfill(3)
            instr = Instruction.from_opcode(padded)

            self.prog_ctr += 1
            self.run_instruction(instr)

    def run_instruction(self, instr):
        handler, has_arg = registered_handlers[instr.opname]

        if has_arg:
            if instr.oparg is None:
                raise ValueError("Expected argument to instruction.")

            handler(self, int(instr.oparg))

        else:
            if instr.oparg is not None:
                raise ValueError("Unexpected argument to instruction.")

            handler(self)

    # Everything beyond this point should be instruction handlers:

    @instr_handler("HLT", has_arg=False)
    def halt_instr(self):
        self.running = False

    @instr_handler("ADD", has_arg=True)
    def add_instr(self, address):
        self.accumulator += self.memory[address]

        # TODO: for this and SUB, allow a choice
        # of overflowing or capping the value
        if self.accumulator > 999:
            self.accumulator = 999

    @instr_handler("SUB", has_arg=True)
    def sub_instr(self, address):
        self.accumulator -= self.memory[address]
        if self.accumulator < -999:
            self.accumulator = -999

    @instr_handler("STA", has_arg=True)
    @instr_handler("STO", has_arg=True)
    def store_instr(self, address):
        self.memory[address] = self.accumulator

    @instr_handler("LDA", has_arg=True)
    def load_instr(self, address):
        self.accumulator = self.memory[address]

    @instr_handler("BRA", has_arg=True)
    def branch_instr(self, address):
        self.prog_ctr = address

    @instr_handler("BRZ", has_arg=True)
    def branch_if_zero_instr(self, address):
        if self.accumulator == 0:
            self.prog_ctr = address

    @instr_handler("BRP", has_arg=True)
    def branch_if_positive_instr(self, address):
        if self.accumulator >= 0:
            self.prog_ctr = address

    @instr_handler("INP", has_arg=False)
    def input_instr(self):
        self.accumulator = int(input("> "))

    @instr_handler("OUT", has_arg=False)
    def output_instr(self):
        self.output += str(self.accumulator)

    @instr_handler("OTC", has_arg=False)
    def output_char_instr(self):
        self.output += chr(self.accumulator)
