from abc import ABC, abstractmethod


class OpcodeHandler(ABC):
    def __init__(self, next_handler=None):
        self.next_handler = next_handler

    def handle(self, instruction: str):
        if self._check_opcode(instruction):
            return self._generate_bytes(instruction)
        elif self.next_handler:
            return self.next_handler.handle(instruction)
        else:
            raise ValueError(f"Unknown instruction: {instruction}")

    @abstractmethod
    def _check_opcode(self, instruction):
        pass

    @abstractmethod
    def _generate_bytes(self, instruction):
        pass


class ClsHandler(OpcodeHandler):
    def _check_opcode(self, instruction):
        return instruction == "CLS"

    def _generate_bytes(self, instruction):
        return (0x00E0).to_bytes(2, "big")


class RetHandler(OpcodeHandler):
    def _check_opcode(self, instruction):
        return instruction == "RET"

    def _generate_bytes(self, instruction):
        return (0x00EE).to_bytes(2, "big")


class JpHandler(OpcodeHandler):
    def _check_opcode(self, instruction):
        parts = instruction.split()
        return parts[0] == "JP" and len(parts) == 2

    def _generate_bytes(self, instruction):
        parts = instruction.split()
        addr = int(parts[1], 16)
        opcode = 0x1000 | addr
        return opcode.to_bytes(2, "big")


class CallHandler(OpcodeHandler):
    def _check_opcode(self, instruction):
        parts = instruction.split()
        return parts[0] == "CALL" and len(parts) == 2

    def _generate_bytes(self, instruction):
        parts = instruction.split()
        addr = int(parts[1], 16)
        opcode = 0x2000 | addr
        return opcode.to_bytes(2, "big")


class DxynHandler(OpcodeHandler):
    def _check_opcode(self, instruction):
        parts = instruction.split()
        return parts[0] == "DXYN" and len(parts) == 4

    def _generate_bytes(self, instruction):
        parts = instruction.split()
        x = int(parts[1], 16)
        y = int(parts[2], 16)
        n = int(parts[3], 16)
        opcode = 0xD000 | (x << 8) | (y << 4) | n
        return opcode.to_bytes(2, "big")


class LdHandler(OpcodeHandler):
    def _check_opcode(self, instruction):
        parts = instruction.split()
        return parts[0] == "LD" and len(parts) == 3

    def _generate_bytes(self, instruction):
        parts = instruction.split()
        register = int(parts[1][1:], 16)
        value = int(parts[2], 16)
        opcode = 0x6000 | (register << 8) | value
        return opcode.to_bytes(2, "big")


class LdIHandler(OpcodeHandler):
    def _check_opcode(self, instruction):
        parts = instruction.split()
        return parts[0] == "LD" and parts[1] == "I" and len(parts) == 3

    def _generate_bytes(self, instruction):
        parts = instruction.split()
        addr = int(parts[2], 16)
        opcode = 0xA000 | addr
        return opcode.to_bytes(2, "big")


class SknpHandler(OpcodeHandler):
    def _check_opcode(self, instruction):
        parts = instruction.split()
        return parts[0] == "SKNP" and len(parts) == 2

    def _generate_bytes(self, instruction):
        parts = instruction.split()
        register = int(parts[1][1:], 16)
        opcode = 0xE0A1 | (register << 8)
        return opcode.to_bytes(2, "big")


# Update the OpcodeEmitter class
class OpcodeEmitter:
    def __init__(self):
        self.handlers = ClsHandler(
            RetHandler(
                JpHandler(
                    CallHandler(DxynHandler(LdHandler(LdIHandler(SknpHandler()))))
                )
            )
        )

    def emit(self, instruction):
        return self.handlers.handle(instruction)


def parse_instruction(instruction):
    """
    Parse a single instruction and return the corresponding opcode bytes.
    """
    parts = instruction.split()
    opcode = None

    if parts[0] == "CLS":
        opcode = 0x00E0
    elif parts[0] == "RET":
        opcode = 0x00EE
    elif parts[0] == "JP" and len(parts) == 2:
        addr = int(parts[1], 16)
        opcode = 0x1000 | addr
    elif parts[0] == "CALL" and len(parts) == 2:
        addr = int(parts[1], 16)
        opcode = 0x2000 | addr
    else:
        raise ValueError(f"Unknown instruction: {instruction}")

    # Convert opcode to bytes
    return opcode.to_bytes(2, "big")


def assemble_chip8_program(program_str: str):
    instructions = program_str.strip().split("\n")
    bytecode = bytearray()
    emitter = OpcodeEmitter()

    for instruction in instructions:
        opcode_bytes = emitter.emit(instruction)
        bytecode.extend(opcode_bytes)

    return bytecode


def write_to_file(filename, data):
    """
    Write the given data to a binary file.
    """
    with open(filename, "wb") as f:
        f.write(data)


# Example program
program_str = """
CLS
JP 200
CALL 2A2
RET
"""

# Assemble and write to file
bytecode = assemble_chip8_program(program_str)
write_to_file("output.ch8", bytecode)
print("Program assembled and written to output.ch8")
