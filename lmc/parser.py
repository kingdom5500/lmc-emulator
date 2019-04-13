from utils import all_opcodes, Instruction, raise_parsing_error

COMMENT_STARTERS = ("#", "//")


def _remove_comments(line):
    """
    Remove any comments from a line.

    The `starters` argument defines how comments should
    start. Nothing else is removed from the line. The
    return value is a tuple in the form (code, comment).
    """

    first_start = COMMENT_STARTERS[0]

    for start in COMMENT_STARTERS:
        line = line.replace(start, first_start)

    parts = line.split(first_start, 1)

    if len(parts) == 1:
        return (parts[0], "")

    return tuple(parts)


def _get_raw_assembly(string):
    """
    Yield each instruction line as a tuple of parts.

    This will strip comments and whitespace before yielding
    each whitespace-separated part as a tuple. No validation
    on the parts is performed.
    """

    line = ""
    for index, char in enumerate(string):
        if char in "\r\n" or index == len(string) - 1:
            code, _ = _remove_comments(line)

            parts = code.strip().split()
            if parts:
                yield tuple(parts)

            line = ""

        line += char


def _scan_for_labels(string):
    """
    Scan an assembly string for its labels.

    This will return a dictionary whose content is in
    the form {label_name: address}.

    Labels are considered to be case-sensitive, so having
    both "MAIN" and "main" as labels would be perfectly
    valid. However, if two label names are identical, a
    ValueError is raised.
    """

    labels = {}

    for addr, parts in enumerate(_get_raw_assembly(string)):
        # Lines with only one part cannot have labels. Skip 'em.
        if len(parts) == 1:
            continue

        # For lines with two parts, the first part is considered
        # to be a label if it is not a valid instruction name.
        elif len(parts) == 2:
            if parts[0] not in all_opcodes:
                label = parts[0]
            else:
                continue

        # Lines with three parts have a label at the first part.
        elif len(parts) == 3:
            label = parts[0]

            # The label must not use a reserved instruction name.
            if label in all_opcodes:
                raise ValueError("Invalid label name " + repr(label))

        if label in labels:
            raise ValueError("Duplicate label " + repr(label))

        labels[label] = addr

    return labels


def parse_assembly(string):
    """
    Parse an assembly string into Instructions.

    This uses generators as much as possible so that memory
    usage stays at a minimum. However, it's hardly a concern
    as LMC programs shouldn't be more than 100 instructions.
    Still, this is supposed to be highly expandable, and it
    doesn't hurt readability to do it this way at all.
    """

    labels = _scan_for_labels(string)

    def _resolve_argument(oparg):
        """
        Simply convert an argument into an address.

        This does nothing if the argument is an integer, but
        will convert labels into addresses where necessary.
        A ValueError may be raised for unknown labels.
        """

        try:
            address = int(oparg)
        except ValueError:
            address = labels.get(oparg)

        if address is None:
            raise raise_parsing_error("Invalid label " + repr(oparg))

        return address

    for parts in _get_raw_assembly(string):
        if len(parts) == 1:
            # Simple enough, just an 'INSTR' line.
            opname = parts[0]
            if opname not in all_opcodes:
                raise_parsing_error("Invalid instruction.", index)

            yield Instruction(opname, None)

        elif len(parts) == 2:
            if not any(part in all_opcodes for part in parts):
                raise_parsing_error("Invalid instruction.", index)

            # Check if we've got a 'LABEL INSTR' line.
            if parts[0] not in all_opcodes:
                yield Instruction(parts[1], None)

            # Or maybe we've got a 'INSTR ARG' line.
            elif parts[1] not in all_opcodes:
                opname, oparg = parts
                yield Instruction(opname, _resolve_argument(oparg))

            else:
                raise_parsing_error("Invalid instruction.", index)

        elif len(parts) == 3:
            # This is also easy, it's always 'LABEL INSTR ARG'.
            label, opname, oparg = parts
            yield Instruction(opname, _resolve_argument(oparg))


def parse_assembly_file(file_path):
    """
    Parse an assembly file into Instructions.

    Refer to `parse_assembly` for further information.
    """

    with open(file_path) as asm_file:
        yield from parse_assembly(asm_file.read())
