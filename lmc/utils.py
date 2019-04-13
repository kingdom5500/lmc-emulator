import re
from collections import namedtuple

OPCODES_FILE = "opcodes.cfg"
PLACEHOLDER = "x"

BaseInstruction = namedtuple("BaseInstruction", "opname oparg")


class Instruction(BaseInstruction):
    def full_opcode(self):
        opcode_base = all_opcodes[self.opname]
        max_arg_size = opcode_base.count(PLACEHOLDER)

        oparg = str(self.oparg if self.oparg is not None else "")
        if len(oparg) > max_arg_size:
            raise ValueError("Opcode argument is too large.")

        padded_oparg = oparg.zfill(max_arg_size)

        opcode = ""
        for char in opcode_base:
            if char == PLACEHOLDER:
                opcode += padded_oparg
                break

            opcode += char

        return opcode

    @classmethod
    def from_opcode(cls, opcode):
        opcode = str(opcode)

        if len(opcode) != 3:
            raise ValueError("Invalid opcode size.")

        best_match = None
        best_size = 0

        for opname, opcode_base in all_opcodes.items():
            op_start = opcode_base.rstrip(PLACEHOLDER)
            match_object = re.match(op_start, opcode)

            if match_object is None:
                continue

            match = match_object.group(0)

            if len(match) > best_size:
                best_match = opname
                best_size = len(match)

            if best_size == 3:
                break

        if best_match is None:
            return None

        arg_size = all_opcodes[best_match].count(PLACEHOLDER)
        if arg_size > 0:
            oparg = opcode[-arg_size:]
        else:
            oparg = None

        return cls(best_match, oparg)


def raise_parsing_error(msg, line=None):
    if line is not None:
        msg += " (instruction {})".format(line)

    raise ValueError(msg)


def _parse_opcodes_file():
    """Parse the opcodes file into a dictionary."""

    opcode_lookup = {}

    with open(OPCODES_FILE) as config:
        for index, line in enumerate(config, 1):
            info = line.split("#", 1)[0]  # Remove any comments.

            if not info.strip():
                continue  # Blank line.

            parts = info.split(":")
            if len(parts) != 2:
                raise_parsing_error("Invalid opcode definition.", index)

            opname, opcode = parts
            opname = opname.strip().upper()
            opcode = opcode.strip().lower()

            # The placeholder must be contiguous and at the end.
            if not opcode.endswith(opcode.count(PLACEHOLDER) * PLACEHOLDER):
                raise_parsing_error("Invalid opcode placeholders", index)

            if opcode.count(PLACEHOLDER) != len(opcode):
                valid_number = opcode.rstrip(PLACEHOLDER).isdigit()
                if not opname.isalpha() or not valid_number:
                    raise_parsing_error("Invalid opname or opcode.", index)

            if len(opcode) != 3:
                raise_parsing_error("Invalid opcode length.", index)

            if opname in opcode_lookup:
                raise_parsing_error("Duplicate opname.", index)

            opcode_lookup[opname] = opcode

    return opcode_lookup


registered_handlers = {}


def instr_handler(opname, *, has_arg=True):

    def wrapper(method):
        registered_handlers[opname] = (method, has_arg)
        return method

    return wrapper


all_opcodes = _parse_opcodes_file()
