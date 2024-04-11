import random
import pygame


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
           0xF0, 0x80, 0xF0, 0x80, 0x80]  # F

# Define a mapping from Pygame key constants to Chip-8 keys
KEY_MAP = {
    pygame.K_1: 0x1,
    pygame.K_2: 0x2,
    pygame.K_3: 0x3,
    pygame.K_4: 0xC,
    pygame.K_q: 0x4,
    pygame.K_w: 0x5,
    pygame.K_e: 0x6,
    pygame.K_r: 0xD,
    pygame.K_a: 0x7,
    pygame.K_s: 0x8,
    pygame.K_d: 0x9,
    pygame.K_f: 0xE,
    pygame.K_z: 0xA,
    pygame.K_x: 0x0,
    pygame.K_c: 0xB,
    pygame.K_v: 0xF,
}


class Chip8:
    def __init__(self):
        self.opcode = 0
        self.memory = [0] * 4096
        self.V = [0] * 16  # V registers
        self.I = 0  # Index register
        self.pc = 0x200  # Program counter starts at 0x200
        self.gfx = [[0 for _ in range(64)] for _ in range(32)]
        self.delay_timer = 0
        self.sound_timer = 0
        self.stack = [0] * 16
        self.sp = 0  # Stack pointer
        self.keypad = [0] * 16
        self.draw_flag = True
        self.keys = [0] * 16
        for i in range(80):  # Load fontset
            self.memory[i] = fontset[i]

    def load_rom(self, filename):
        """Load a Chip-8 ROM into memory."""
        with open(filename, "rb") as f:
            rom_data = f.read()
            for i, byte in enumerate(rom_data):
                self.memory[0x200 + i] = byte

    def emulate_cycle(self):
        """Fetch, decode, and execute one opcode."""
        # Fetch
        opcode = (self.memory[self.pc] << 8) | self.memory[self.pc + 1]

        # Decode & Execute
        if opcode & 0xF000 == 0x1000:  # JP addr
            self.pc = opcode & 0x0FFF

        elif opcode == 0x00EE:  # RET opcode
            self.sp -= 1
            self.pc = self.stack[self.sp]
            self.pc += 2


        elif opcode & 0xF000 == 0x2000:  # CALL addr
            self.stack[self.sp] = self.pc
            self.sp += 1
            self.pc = opcode & 0x0FFF

        elif opcode & 0xF000 == 0x3000:  # SE Vx, byte
            reg = (opcode & 0x0F00) >> 8
            if self.V[reg] == (opcode & 0x00FF):
                self.pc += 4
            else:
                self.pc += 2

        elif opcode & 0xF000 == 0x4000:  # SNE Vx, byte
            reg = (opcode & 0x0F00) >> 8
            if self.V[reg] != (opcode & 0x00FF):
                self.pc += 4
            else:
                self.pc += 2

        elif opcode & 0xF000 == 0x5000:  # SE Vx, Vy
            x = (opcode & 0x0F00) >> 8
            y = (opcode & 0x00F0) >> 4
            if self.V[x] == self.V[y]:
                self.pc += 4
            else:
                self.pc += 2

        elif opcode & 0xF000 == 0x6000:  # LD Vx, byte
            x = (opcode & 0x0F00) >> 8
            self.V[x] = opcode & 0x00FF
            self.pc += 2

        elif opcode & 0xF000 == 0x7000:  # ADD Vx, byte
            x = (opcode & 0x0F00) >> 8
            self.V[x] += opcode & 0x00FF
            self.V[x] &= 0xFF  # Ensure it doesn't exceed 8 bits
            self.pc += 2

        elif opcode & 0xF00F == 0x8000:  # LD Vx, Vy
            x = (opcode & 0x0F00) >> 8
            y = (opcode & 0x00F0) >> 4
            self.V[x] = self.V[y]
            self.pc += 2

        elif opcode & 0xF00F == 0x8001:  # OR Vx, Vy
            x = (opcode & 0x0F00) >> 8
            y = (opcode & 0x00F0) >> 4
            self.V[x] |= self.V[y]
            self.pc += 2

        elif opcode & 0xF00F == 0x8002:  # AND Vx, Vy
            x = (opcode & 0x0F00) >> 8
            y = (opcode & 0x00F0) >> 4
            self.V[x] &= self.V[y]
            self.pc += 2

        elif opcode & 0xF00F == 0x8003:  # XOR Vx, Vy
            x = (opcode & 0x0F00) >> 8
            y = (opcode & 0x00F0) >> 4
            self.V[x] ^= self.V[y]
            self.pc += 2

        elif opcode & 0xF00F == 0x8004:  # ADD Vx, Vy with carry
            x = (opcode & 0x0F00) >> 8
            y = (opcode & 0x00F0) >> 4
            result = self.V[x] + self.V[y]
            self.V[0xF] = (
                1 if result > 0xFF else 0
            )  # Set VF to 1 if there's a carry, else 0
            self.V[x] = result & 0xFF
            self.pc += 2

        elif opcode & 0xF0FF == 0xE09E:  # SKP Vx
            x = (opcode & 0x0F00) >> 8
            if self.keys[self.V[x]] == 1:
                self.pc += 4
            else:
                self.pc += 2

        elif opcode & 0xF0FF == 0xE0A1:  # SKNP Vx
            x = (opcode & 0x0F00) >> 8
            if self.keys[self.V[x]] == 0:
                self.pc += 4
            else:
                self.pc += 2

        elif opcode & 0xF00F == 0x8005:  # SUB Vx, Vy
            x = (opcode & 0x0F00) >> 8
            y = (opcode & 0x00F0) >> 4
            self.V[0xF] = 1 if self.V[x] > self.V[y] else 0
            self.V[x] -= self.V[y]
            self.V[x] &= 0xFF
            self.pc += 2

        elif opcode & 0xF00F == 0x8006:  # SHR Vx {, Vy}
            x = (opcode & 0x0F00) >> 8
            self.V[0xF] = self.V[x] & 0x1
            self.V[x] >>= 1
            self.pc += 2

        elif opcode & 0xF00F == 0x8007:  # SUBN Vx, Vy
            x = (opcode & 0x0F00) >> 8
            y = (opcode & 0x00F0) >> 4
            self.V[0xF] = 1 if self.V[y] > self.V[x] else 0
            self.V[x] = self.V[y] - self.V[x]
            self.V[x] &= 0xFF
            self.pc += 2

        elif opcode & 0xF00F == 0x800E:  # SHL Vx {, Vy}
            x = (opcode & 0x0F00) >> 8
            self.V[0xF] = (self.V[x] & 0x80) >> 7
            self.V[x] <<= 1
            self.V[x] &= 0xFF
            self.pc += 2

        elif opcode & 0xF00F == 0x9000:  # SNE Vx, Vy
            x = (opcode & 0x0F00) >> 8
            y = (opcode & 0x00F0) >> 4
            if self.V[x] != self.V[y]:
                self.pc += 4
            else:
                self.pc += 2

        elif opcode & 0xF000 == 0xA000:  # LD I, addr
            self.I = opcode & 0x0FFF
            self.pc += 2

        elif opcode & 0xF000 == 0xB000:  # JP V0, addr
            self.pc = (opcode & 0x0FFF) + self.V[0]

        elif opcode & 0xF000 == 0xC000:  # RND Vx, byte
            x = (opcode & 0x0F00) >> 8
            byte_val = opcode & 0x00FF
            self.V[x] = random.randint(0, 255) & byte_val
            self.pc += 2

        elif opcode & 0xF000 == 0xD000:  # DRW Vx, Vy, nibble
            x = self.V[(opcode & 0x0F00) >> 8]
            y = self.V[(opcode & 0x00F0) >> 4]
            height = opcode & 0x000F
            self.V[0xF] = 0
            for row in range(height):
                sprite = self.memory[self.I + row]
                for col in range(8):
                    if 0 <= (y + row) < 32 and 0 <= (x + col) < 64:  # Boundary check
                        if (sprite & (0x80 >> col)) != 0:
                            if self.gfx[y + row][x + col] == 1:
                                self.V[0xF] = 1
                            self.gfx[y + row][x + col] ^= 1
            self.draw_flag = True
            self.pc += 2


        elif opcode & 0xF0FF == 0xF007:  # LD Vx, DT
            x = (opcode & 0x0F00) >> 8
            self.V[x] = self.delay_timer
            self.pc += 2

        elif opcode & 0xF0FF == 0xF00A:  # LD Vx, K
            x = (opcode & 0x0F00) >> 8
            key_pressed = False
            for i in range(len(self.keys)):
                if self.keys[i] == 1:
                    self.V[x] = i
                    key_pressed = True
            if not key_pressed:
                return
            self.pc += 2

        elif opcode & 0xF0FF == 0xF015:  # LD DT, Vx
            x = (opcode & 0x0F00) >> 8
            self.delay_timer = self.V[x]
            self.pc += 2

        elif opcode & 0xF0FF == 0xF018:  # LD ST, Vx
            x = (opcode & 0x0F00) >> 8
            self.sound_timer = self.V[x]
            self.pc += 2

        elif opcode & 0xF0FF == 0xF01E:  # ADD I, Vx
            x = (opcode & 0x0F00) >> 8
            self.I += self.V[x]
            self.pc += 2

        elif opcode & 0xF0FF == 0xF029:  # LD F, Vx
            x = (opcode & 0x0F00) >> 8
            self.I = self.V[x] * 5
            self.pc += 2

        elif opcode & 0xF0FF == 0xF033:  # LD B, Vx
            x = (opcode & 0x0F00) >> 8
            value = self.V[x]
            self.memory[self.I + 2] = value % 10
            value //= 10
            self.memory[self.I + 1] = value % 10
            value //= 10
            self.memory[self.I] = value % 10
            self.pc += 2

        elif opcode & 0xF0FF == 0xF055:  # LD [I], Vx
            x = (opcode & 0x0F00) >> 8
            for i in range(x + 1):
                self.memory[self.I + i] = self.V[i]
            self.pc += 2

        elif opcode & 0xF0FF == 0xF065:  # LD Vx, [I]
            x = (opcode & 0x0F00) >> 8
            for i in range(x + 1):
                self.V[i] = self.memory[self.I + i]
            self.pc += 2

        else:
            print(f"Unknown opcode: {opcode:04X}")
            self.pc += 2

    def update_timers(self):
        if self.delay_timer > 0:
            self.delay_timer -= 1
        if self.sound_timer > 0:
            self.sound_timer -= 1

    def run(self):
        pygame.init()
        window_size = (640, 320)
        screen = pygame.display.set_mode(window_size)
        pygame.display.set_caption("Chip-8 Emulator")
        clock = pygame.time.Clock()

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN or event.type == pygame.KEYUP:
                    key_action = 1 if event.type == pygame.KEYDOWN else 0
                    if event.key in KEY_MAP:
                        self.keypad[KEY_MAP[event.key]] = key_action

            self.emulate_cycle()
            self.update_timers()

            if self.draw_flag:
                self.draw_graphics(screen)
                pygame.display.flip()
                self.draw_flag = False

            clock.tick(60)  # Capping the frame rate at 60fps.

        pygame.quit()


    def draw_graphics(self, screen):
        # If experiencing flickering, consider clearing the screen here.
        for y in range(32):
            for x in range(64):
                color = (255, 255, 255) if self.gfx[y][x] == 1 else (0, 0, 0)
                pygame.draw.rect(screen, color, pygame.Rect(x * 10, y * 10, 10, 10))


if __name__ == "__main__":
    # input to receive via command line the name of the rom
    input_rom = input("Enter the name of the rom: ")
    emulator = Chip8()
    emulator.load_rom(f"games_roms/{input_rom}")
    emulator.run()
