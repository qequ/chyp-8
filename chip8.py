from random import randint

fontset = [0xF0, 0x90, 0x90, 0x90, 0xF0,  # 0
           0x20, 0x60, 0x20, 0x20, 0x70,  # 1
           0xF0, 0x10, 0xF0, 0x80, 0xF0,  # 2
           0xF0, 0x10, 0xF0, 0x10, 0xF0,  # 3
           0x90, 0x90, 0xF0, 0x10, 0x10,  # 4
           0xF0, 0x80, 0xF0, 0x10, 0xF0,  # 5
           0xF0, 0x80, 0xF0, 0x90, 0xF0,  # 6
           0xF0, 0x10, 0x20, 0x40, 0x40,  # 7
           0xF0, 0x90, 0xF0, 0x90, 0xF0,  # 8
           0xF0, 0x90, 0xF0, 0x10, 0xF0,  # 9
           0xF0, 0x90, 0xF0, 0x90, 0x90,  # A
           0xE0, 0x90, 0xE0, 0x90, 0xE0,  # B
           0xF0, 0x80, 0x80, 0x80, 0xF0,  # C
           0xE0, 0x90, 0x90, 0x90, 0xE0,  # D
           0xF0, 0x80, 0xF0, 0x80, 0xF0,  # E
           0xF0, 0x80, 0xF0, 0x80, 0x80  # F
           ]


class Chip8():
    def __init__(self):
        self.opcode = 0
        self.memory = [0]*4096
        # V == registers
        self.V = [0]*16
        self.I = 0  # Index register
        self.pc = 0x200  # program counter
        self.gfx = [0] * 64*32  # pixel setting on screen
        self.delay_timer = 0
        self.sound_timer = 0
        self.stack = [0] * 16  # for jumping
        self.sp = 0  # stack pointer
        self.keypad = [0]*16  # to check if keys were pressed
        self.draw_flag = True

        for i in range(len(fontset)):
            # loading the fontset in memory
            self.memory[i] = fontset[i]

    def emulate_cycle(self):
        # fetch
        self.opcode = self.memory[self.pc] << 8 | self.memory[self.pc+1]

        # decode and execute
        mask = self.opcode & 0xF000  # mask for keeping the most significant byte
        x = (self.opcode & 0x0F00) >> 8
        y = (self.opcode & 0x00F0) >> 4
        nnn = self.opcode & 0x0FFF
        kk = self.opcode & 0x00FF

        if mask == 0x0000:
            if self.opcode == 0x00E0:
                for i in range(len(self.gfx)):
                    self.gfx[i] = 0x0
                self.draw_flag = True
                self.pc += 2  # jumping to the next instruction

            elif self.opcode == 0x00EE:
                self.sp -= 1
                self.pc = self.stack[self.sp]  # returning from subroutine
                self.pc += 2
            else:
                print("{} SYS instruction - not used anymore".format(self.opcode))
        elif mask == 0x1000:
            # jumping to the address nnn
            self.pc = nnn
        elif mask == 0x2000:
            # jumping to subroutine at nnn
            self.stack[self.sp] = self.pc
            self.sp += 1
            self.pc = nnn
        elif mask == 0x3000:
            # The interpreter compares register Vx to kk, and if they are equal, increments the program counter by 2.
            if self.V[x] == kk:
                self.pc += 4
            else:
                self.pc += 2
        elif mask == 0x4000:
            #  The interpreter compares register Vx to kk, and if they are not equal, increments the program counter by 2.
            if self.V[x] != kk:
                self.pc += 4
            else:
                self.pc += 2

        elif mask == 0x5000:
            # The interpreter compares register Vx to register Vy, and if they are equal, increments the program counter by 2.
            if self.V[x] == self.V[y]:
                self.pc += 4
            else:
                self.pc += 2

        elif mask == 0x6000:
            #  The interpreter puts the value kk into register Vx.
            self.V[x] = kk
            self.pc += 2

        elif mask == 0x7000:
            #  Adds the value kk to the value of register Vx, then stores the result in Vx.
            self.V[x] += kk
            self.pc += 2
        elif mask == 0x8000:
            mask2 = self.opcode & 0x000F
            if mask2 == 0x0000:
                # Stores the value of register Vy in register Vx.
                self.V[x] = self.V[y]
                self.pc += 2

            elif mask2 == 0x0001:
                # Set Vx = Vx OR Vy. Performs a bitwise OR on the values of Vx and Vy, then stores the result in Vx.
                self.V[x] |= self.V[y]
                self.pc += 2

            elif mask2 == 0x0002:
                # Performs a bitwise AND on the values of Vx and Vy, then stores the result in Vx.
                self.V[x] &= self.V[y]
                self.pc += 2

            elif mask2 == 0x0003:
                # Performs a bitwise exclusive OR on the values of Vx and Vy, then stores the result in Vx.
                self.V[x] ^= self.V[y]
                self.pc += 2

            elif mask2 == 0x0004:
                # The values of Vx and Vy are added together.
                # If the result is greater than 8 bits (i.e., > 255,) VF is set to 1, otherwise 0.
                # Only the lowest 8 bits of the result are kept, and stored in Vx.
                if self.V[x] + self.V[y] > 0xFF:
                    self.V[0xF] = 1
                else:
                    self.V[0xF] = 0

                self.V[x] += self.V[y]
                self.pc += 2

            elif mask2 == 0x0005:
                # If Vx > Vy, then VF is set to 1, otherwise 0. Then Vy is subtracted from Vx, and the results stored in Vx.
                if self.V[x] > self.V[y]:
                    self.V[0xF] = 1
                else:
                    self.V[0xF] = 0
                self.V[x] -= self.V[y]
                self.pc += 2

            elif mask2 == 0x0006:
                # If the least-significant bit of Vx is 1, then VF is set to 1, otherwise 0. Then Vx is divided by 2.
                self.V[0xF] = self.V[x] & 0x1
                self.V[x] >>= 1
                self.pc += 2

            elif mask2 == 0x0007:
                # If Vy > Vx, then VF is set to 1, otherwise 0. Then Vx is subtracted from Vy, and the results stored in Vx.
                if self.V[y] > self.V[x]:
                    self.V[0xF] = 1
                else:
                    self.V[0xF] = 0
                self.V[x] = self.V[y] - self.V[x]
                self.pc += 2

            elif mask2 == 0x000E:
                # If the most-significant bit of Vx is 1, then VF is set to 1, otherwise to 0. Then Vx is multiplied by 2.
                self.V[0xF] = self.V[x] >> 7
                self.V[x] <<= 1
                self.pc += 2
            else:
                print('{} - Wrong opcode'.format(hex(self.opcode)))
        elif mask == 0x9000:
            # Skip next instruction if Vx != Vy.
            if self.V[x] != self.V[y]:
                self.pc += 4
            else:
                self.pc += 2

        elif mask == 0xA000:
            # The value of register I is set to nnn.
            self.I = nnn
            self.pc += 2

        elif mask == 0xB000:
            # Jump to location nnn + V0.
            self.pc = self.V[0] + nnn

        elif mask == 0xC000:
            #  The interpreter generates a random number from 0 to 255, which is then ANDed with the value kk.
            # The results are stored in Vx. See instruction 8xy2 for more information on AND.
            self.V[x] = randint(0, 255) & kk
            self.pc += 2

        elif mask == 0xD000:
            print('{} - DRW V{}, V{}, {} - Display {}-byte sprite starting at memory lself.opcodeation I at (V{}, V{}), set VF = collision.'.format(
                hex(self.opcode), x, y, (self.opcode & 0x000F), (self.opcode & 0x000F), x, y))
        elif mask == 0xE000:
            mask2 = self.opcode & 0x00FF
            if mask2 == 0x009E:
                print(
                    '{} - SKP V{} - Skip next instruction if key with the value of V{} is pressed.'.format(hex(self.opcode), x, x))
            elif mask2 == 0x00A1:
                print(
                    '{} - SKNP V{} - Skip next instruction if key with the value of V{} is not pressed.'.format(hex(self.opcode), x, x))
            else:
                print('{} - Wrong opcode'.format(hex(self.opcode)))

        elif mask == 0xF000:
            mask2 = self.opcode & 0x00FF

            if mask2 == 0x0007:
                print(
                    '{} - LD V{}, DT - Set V{} = delay timer value.'.format(hex(self.opcode), x, x))
            elif mask2 == 0x000A:
                print(
                    '{} - LD V{}, K - Wait for a key press, store the value of the key in V{}.'.format(hex(self.opcode), x, x))
            elif mask2 == 0x0015:
                print(
                    '{} - LD DT, V{} - Set delay timer = V{}.'.format(hex(self.opcode), x, x))
            elif mask2 == 0x0018:
                print(
                    '{} - LD ST, V{} - Set sound timer = V{}.'.format(hex(self.opcode), x, x))
            elif mask2 == 0x001E:
                print(
                    '{} - ADD I, V{} - Set I = I + V{}.'.format(hex(self.opcode), x, x))
            elif mask2 == 0x0029:
                print(
                    '{} - LD F, V{} - Set I = lself.opcodeation of sprite for digit V{}.'.format(hex(self.opcode), x, x))
            elif mask2 == 0x0033:
                print(
                    '{} - LD B, V{} - Store BCD representation of V{} in memory lself.opcodeations I, I+1, and I+2.'.format(hex(self.opcode), x, x))
            elif mask2 == 0x0055:
                print(
                    '{} - LD [I], V{} - Store registers V0 through V{} in memory starting at lself.opcodeation I.'.format(hex(self.opcode), x, x))
            elif mask2 == 0x0065:
                print(
                    '{} - LD V{}, [I] - Read registers V0 through V{} from memory starting at lself.opcodeation I.'.format(hex(self.opcode), x, x))
            else:
                print('{} - Wrong opcode'.format(hex(self.opcode)))
