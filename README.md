# chyp-8
An implementation of the classic CHIP-8 virtual machine in Python.

## Project Overview
This project is a Python-based implementation of the CHIP-8 virtual machine. CHIP-8 is an interpreted programming language that was first used in the mid-1970s. It was initially used on 8-bit microcomputers and has since become a popular choice for creating simple video games.

Our implementation, chyp-8, provides a complete virtual machine that can interpret and execute CHIP-8 programs. It includes a CPU emulator, memory management, and input/output handling.

## Tools
### Assembler
The assembler is a tool that translates CHIP-8 assembly language into machine code that can be executed by the CHIP-8 virtual machine. It takes a text file containing CHIP-8 assembly instructions as input and outputs a binary file containing the corresponding machine code.

### Disassembler
The disassembler does the opposite of the assembler. It takes a binary file containing CHIP-8 machine code as input and outputs a text file containing the corresponding assembly instructions. This can be useful for understanding how a particular CHIP-8 program works.

## Usage
To assemble a CHIP-8 program, run the assembler with the input and output files as arguments:

```bash
python assembler.py input.ch8 output.ch8
```

To disassemble a CHIP-8 program, run the disassembler with the input and output files as arguments:

```bash
python disassembler.py input.ch8
```

To run a CHIP-8 program, run the virtual machine with the program file as an argument:

```bash
python chyp8.py program.ch8
```

## Contributing
Contributions are welcome!

## License
This project is licensed under the MIT License. See the LICENSE file for more information.
