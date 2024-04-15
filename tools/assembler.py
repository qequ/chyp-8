import argparse
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
        return parts[0].startswith("D") and len(parts[0]) == 4

    def _generate_bytes(self, instruction):
        parts = instruction.split()
        x = int(parts[0][1], 16)
        y = int(parts[0][2], 16)
        n = int(parts[0][3], 16)
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
        register = int(parts[1][1:], 16)  # Extract the 'x' from 'Vx'
        opcode = 0xE0A1 | (register << 8)
        return opcode.to_bytes(2, "big")


# Update the OpcodeEmitter class
class OpcodeEmitter:
    def __init__(self):
        # TODO - Add all the handlers
        self.handlers = ClsHandler(
            RetHandler(
                JpHandler(
                    CallHandler(DxynHandler(LdIHandler(LdHandler(SknpHandler()))))
                )
            )
        )

    def emit(self, instruction):
        return self.handlers.handle(instruction)


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


def main():
    parser = argparse.ArgumentParser(description="Assemble a CHIP-8 program.")
    parser.add_argument("input", type=str, help="The input CHIP-8 program file.")
    parser.add_argument(
        "output", type=str, help="The output file to write the assembled bytecode to."
    )
    args = parser.parse_args()

    with open(args.input, "r") as f:
        program_str = f.read()

    bytecode = assemble_chip8_program(program_str)

    write_to_file(args.output, bytecode)
    print(f"Program assembled and written to {args.output}")


if __name__ == "__main__":
    main()
