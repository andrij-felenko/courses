# gen_table.py — генератор таблиці слів BSRR (запускається один раз при складанні)
import math

LEN     = 256                       # точок на період
PINMAP  = [0, 1, 4, 5, 6, 7, 8, 9]  # b0…b7 → номери виводів у групі порту
ALL     = sum(1 << p for p in PINMAP)

def bsrr(value: int) -> int:
    """Слово BSRR: молодша половина ставить одиниці, старша скидає решту наших виводів."""
    set_mask = sum(1 << p for b, p in enumerate(PINMAP) if value & (1 << b))
    return set_mask | ((ALL & ~set_mask) << 16)

words = []
for i in range(LEN):
    s = math.sin(2 * math.pi * (i + 0.5) / LEN)     # +0.5 — відлік у середині кроку
    words.append(bsrr(round(127.5 + 127.5 * s)))    # 0…255 на всю шкалу

with open("sine_bsrr.h", "w", encoding="utf-8") as f:
    f.write("/* Згенеровано gen_table.py — не правити руками. */\n")
    f.write("#include <stdint.h>\n")
    f.write(f"const uint32_t sine_bsrr[{LEN}] = {{\n")
    for i in range(0, LEN, 4):
        f.write("    " + " ".join(f"0x{w:08X}," for w in words[i:i + 4]) + "\n")
    f.write("};\n")
