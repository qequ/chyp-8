
def dissassemble_rom(file):
    with open(file, "rb") as rom:
        data = rom.read()
    data = list(data)

    opcodes = []

    if len(data) % 2 == 1:
        data.append(0x00)

    for i in range(0, len(data), 2):
        # the opcodes are 2 bytes long, as data is stored at 1 byte length
        #  we have to concatenate it
        opcodes.append((data[i] << 8) + data[i+1])

    for oc in opcodes:
        mask = oc & 0xF000
        x = (oc & 0x0F00) >> 8
        y = (oc & 0x00F0) >> 4
        nnn = oc & 0x0FFF
        kk = oc & 0x00FF

        if mask == 0x0000:
            if oc == 0x00E0:
                print('{} - CLS - Clear the display'.format(hex(oc)))
            elif oc == 0x00EE:
                print('{} - RET - Return from a subroutine.'.format(hex(oc)))
        elif mask == 0x1000:
            print('{} - JP {} - Jump to location {}'.format(hex(oc), hex(nnn), hex(nnn)))
        elif mask == 0x2000:
            print(
                '{} - CALL {} - Call subroutine at {}.'.format(hex(oc), hex(nnn), hex(nnn)))
        elif mask == 0x3000:
            print(
                '{} - SE V{}, {} - Skip next instruction if V{} = {}.'.format(hex(oc), x, kk,  x, kk))
        elif mask == 0x4000:
            print('{} - SNE V{}, {} - Skip next instruction if V{} != {}.'.format(
                hex(oc), x, kk, x, kk))
        elif mask == 0x5000:
            print(
                '{} - SE V{}, V{} - Skip next instruction if V{} = V{}.'.format(hex(oc), x, y, x, y))
        elif mask == 0x6000:
            print('{} - LD V{}, {} - Set V{} = {}.'.format(hex(oc), x, kk, x, kk))
        elif mask == 0x7000:
            print(
                '{} - ADD V{}, {} - Set V{} = V{} + {}.'.format(hex(oc), x, kk, x, x, kk))
        elif mask == 0x8000:
            mask2 = oc & 0x000F
            if mask2 == 0x0000:
                print('{} - LD V{}, V{} - Set V{} = V{}.'.format(hex(oc), x, y, x, y))
            elif mask2 == 0x0001:
                print(
                    '{} - OR V{}, V{} - Set V{} = V{} OR V{}.'.format(hex(oc), x, y, x, x, y))
            elif mask2 == 0x0002:
                print(
                    '{} - AND V{}, V{} - Set V{} = V{} AND V{}.'.format(hex(oc), x, y, x, x, y))
            elif mask2 == 0x0003:
                print(
                    '{} - XOR V{}, V{} - Set V{} = V{} XOR V{}.'.format(hex(oc), x, y, x, x, y))
            elif mask2 == 0x0004:
                print(
                    '{} - ADD V{}, V{} Set V{} = V{} + V{}, set VF = carry.'.format(hex(oc), x, y, x, x, y))
            elif mask2 == 0x0005:
                print(
                    '{} - SUB V{}, V{} - Set V{} = V{} - V{}, set VF = NOT borrow.'.format(hex(oc), x, y, x, x, y))
            elif mask2 == 0x0006:
                print(
                    '{} - SHR V{} [ V{}] Set V{} = V{} SHR 1.'.format(hex(oc), x, y, x, x))
            elif mask2 == 0x0007:
                print(
                    '{} - SUBN V{}, V{} Set V{} = V{} - V{}, set VF = NOT borrow.'.format(hex(oc), x, y, x, y, x))
            elif mask2 == 0x000E:
                print(
                    '{} - SHL V{} [, V{}]Set V{} = V{} SHL 1.'.format(hex(oc), x, y, x, x))
            else:
                print('{} - Wrong opcode'.format(hex(oc)))
        elif mask == 0x9000:
            if (oc & 0x000F) == 0x0000:
                print(
                    '{} - SNE V{}, V{} - Skip next instruction if V{} != V{}.'.format(hex(oc), x, y, x, y))
            else:
                print('{} - Wrong opcode'.format(hex(oc)))
        elif mask == 0xA000:
            print('{} - LD I, {} - Set I = {}.'.format(hex(oc), nnn, nnn))
        elif mask == 0xB000:
            print('{} - JP V0, {} - Jump to location {} + V0.'.format(hex(oc), nnn, nnn))
        elif mask == 0xC000:
            print(
                '{} - RND V{}, {} - Set V{} = random byte AND {}.'.format(hex(oc), x, kk, x, kk))
        elif mask == 0xD000:
            print('{} - DRW V{}, V{}, {} - Display {}-byte sprite starting at memory location I at (V{}, V{}), set VF = collision.'.format(
                hex(oc), x, y, (oc & 0x000F), (oc & 0x000F), x, y))
        elif mask == 0xE000:
            mask2 = oc & 0x00FF
            if mask2 == 0x009E:
                print(
                    '{} - SKP V{} - Skip next instruction if key with the value of V{} is pressed.'.format(hex(oc), x, x))
            elif mask2 == 0x00A1:
                print(
                    '{} - SKNP V{} - Skip next instruction if key with the value of V{} is not pressed.'.format(hex(oc), x, x))
            else:
                print('{} - Wrong opcode'.format(hex(oc)))

        elif mask == 0xF000:
            mask2 = oc & 0x00FF

            if mask2 == 0x0007:
                print(
                    '{} - LD V{}, DT - Set V{} = delay timer value.'.format(hex(oc), x, x))
            elif mask2 == 0x000A:
                print(
                    '{} - LD V{}, K - Wait for a key press, store the value of the key in V{}.'.format(hex(oc), x, x))
            elif mask2 == 0x0015:
                print('{} - LD DT, V{} - Set delay timer = V{}.'.format(hex(oc), x, x))
            elif mask2 == 0x0018:
                print('{} - LD ST, V{} - Set sound timer = V{}.'.format(hex(oc), x, x))
            elif mask2 == 0x001E:
                print('{} - ADD I, V{} - Set I = I + V{}.'.format(hex(oc), x, x))
            elif mask2 == 0x0029:
                print(
                    '{} - LD F, V{} - Set I = location of sprite for digit V{}.'.format(hex(oc), x, x))
            elif mask2 == 0x0033:
                print(
                    '{} - LD B, V{} - Store BCD representation of V{} in memory locations I, I+1, and I+2.'.format(hex(oc), x, x))
            elif mask2 == 0x0055:
                print(
                    '{} - LD [I], V{} - Store registers V0 through V{} in memory starting at location I.'.format(hex(oc), x, x))
            elif mask2 == 0x0065:
                print(
                    '{} - LD V{}, [I] - Read registers V0 through V{} from memory starting at location I.'.format(hex(oc), x, x))
            else:
                print('{} - Wrong opcode'.format(hex(oc)))
