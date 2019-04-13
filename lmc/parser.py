from utils import all_opcodes, Instruction, raise_parsing_error


def parse_assembly(string):
    """
    Parse an assembly string.

    This generator function takes a string and will try
    to parse it. If it encounters a syntax error with the
    string, an appropriate `ValueError` will be raised.

    The generator yields `Instruction` objects.
    Labels are converted into addresses in this function,
    so the objects will not contain any label information
    at all.
    """

    # This isn't the most memory-efficient way of parsing the content,
    # but LMC programs can't reach more than 100 instructions so it
    # shouldn't be too bad. Still, it might be a nice idea to parse
    # the content more efficiently with generators and stuff. I think
    # this should also look for labels before fully parsing to avoid
    # sorting them out afterwards.

    labels = {}
    instructions = []  # Stores tuples of (opname, arg, line)
    address = 0

    for index, line in enumerate(string.splitlines(), 1):
        # We're allowing "#" and "//" for comments.
        # TODO: consider a warning when both are used.
        line = line.replace("//", "#").split("#", 1)[0]

        if not line.strip():
            continue

        parts = line.split()
        if not all(part.lstrip("-").isalnum() for part in parts):
            raise_parsing_error("Invalid character.", index)

        if len(parts) == 1:
            # Simple enough, just an 'INSTR' line.
            opname = parts[0]
            if opname not in all_opcodes:
                raise_parsing_error("Invalid instruction.", index)

            instructions.append((opname, None, index))

        elif len(parts) == 2:
            if not any(part in all_opcodes for part in parts):
                raise_parsing_error("Invalid instruction.", index)

            # Check if we've got a 'LABEL INSTR' line.
            if parts[0] not in all_opcodes:
                label, opname = parts

                if label in labels or not label.isalnum():
                    raise_parsing_error("Invalid label.", index)

                labels[label] = address
                instructions.append((opname, None, index))

            # Or maybe we've got a 'INSTR ARG' line.
            elif parts[1] not in all_opcodes:
                opname, oparg = parts
                instructions.append((opname, oparg, index))

            else:
                raise_parsing_error("Invalid instruction.", index)

        elif len(parts) == 3:
            # This is also easy, it's always 'LABEL INSTR ARG'.
            label, opname, oparg = parts

            if label in labels or not label.isalnum():
                raise_parsing_error("Invalid label.", index)

            labels[label] = address
            instructions.append((opname, oparg, index))

        address += 1

    # Okay nice, we've got all of our instructions now.
    # It's time to convert the labels to addresses.
    for instr in instructions:
        opname, oparg, lineno = instr

        if oparg is not None:
            if oparg in labels:
                oparg = labels[oparg]

            elif oparg.lstrip("-").isdigit():
                oparg = int(oparg)

            else:
                raise_parsing_error("Invalid instruction argument.", lineno)

        yield Instruction(opname, oparg)


def parse_assembly_file(file_path):
    """
    Parse an assembly file.

    See `parse_assembly` for further information.
    """

    with open(file_path) as asm_file:
        yield from parse_assembly(asm_file.read())
