#!/usr/bin/env python3
"""gen_crc_table.py — рахує таблицю CRC-32 на машині розробника й пише готовий .c
Запуск:  python3 gen_crc_table.py crc32_table.c"""
import sys

POLY = 0xEDB88320          # CRC-32/ISO-HDLC у відбитому записі
MASK = 0xFFFFFFFF

def build():
    t = []
    for i in range(256):
        c = i
        for _ in range(8):                      # ті самі вісім кроків зсув-XOR
            c = (c >> 1) ^ POLY if c & 1 else c >> 1
        t.append(c & MASK)
    return t

def crc32(data, t):
    crc = MASK
    for b in data:
        crc = (crc >> 8) ^ t[(crc ^ b) & 0xFF]
    return crc ^ MASK

tab = build()
check = crc32(b"123456789", tab)
assert check == 0xCBF43926, "профіль розійшовся: %08X" % check   # ← запобіжник збірки

with open(sys.argv[1], "w") as f:
    f.write("/* ЗГЕНЕРОВАНО gen_crc_table.py — руками не правити. */\n")
    f.write("#include <stdint.h>\n\n")
    f.write("const uint32_t crc32_table[256] = {\n")
    for i in range(0, 256, 4):
        f.write("    " + " ".join("0x%08XU," % v for v in tab[i:i + 4]) + "\n")
    f.write("};\n")
