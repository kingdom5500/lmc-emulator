OPCODES_FILE = "opcodes.cfg"


def _parse_opcodes_file():
    """Parse the opcodes file into a dictionary."""

    opcode_lookup = {}

    with open(OPCODES_FILE) as config:
        for line in config:
            info = line.split("#", 1)[0]  # Remove any comments.

            if not info.strip():
                continue  # Blank line.

            parts = info.split(":")
            if len(parts) != 2:
                raise ValueError(
                    "Invalid opcode definition {opdef} in {file}".format(
                        opdef=repr(info), file=repr(OPCODES_FILE)
                    )
                )

            opname, opcode = parts
            opname = opname.strip().upper()
            opcode = opcode.strip().lower()

            if opname in opcode_lookup:
                raise ValueError(
                    "Duplicate instruction {name} in {file}".format(
                        name=repr(opname), file=repr(OPCODES_FILE)
                    )
                )

            opcode_lookup[opname] = opcode

    return opcode_lookup


all_opcodes = _parse_opcodes_file()
