from collections import namedtuple

OPCODES_FILE = "opcodes.cfg"


def raise_parsing_error(msg, line=None):
    if line is not None:
        msg += " (line {})".format(line)

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

            if not opname.isalpha() or not opcode.replace("x", "").isdigit():
                raise_parsing_error("Invalid opname or opcode.", index)

            if len(opcode) != 3:
                raise_parsing_error("Invalid opcode length.", index)

            if opname in opcode_lookup:
                raise_parsing_error("Duplicate opname.", index)

            opcode_lookup[opname] = opcode

    return opcode_lookup


all_opcodes = _parse_opcodes_file()

Instruction = namedtuple("Instruction", "opname oparg")
