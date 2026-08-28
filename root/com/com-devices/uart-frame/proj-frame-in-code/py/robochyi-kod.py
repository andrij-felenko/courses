from enum import Enum

# Парність байта: XOR усіх 8 біт. Повертає 1, якщо одиниць непарно.
def parity_xor(b: int) -> int:
    b ^= b >> 4          # згортаємо half-байти
    b ^= b >> 2
    b ^= b >> 1
    return b & 1         # лишився XOR усіх вихідних біт

# Біт парності під обрану схему. even: щоб разом стало парно; odd: навпаки.
class Parity(Enum):
    NONE = 0
    EVEN = 1
    ODD  = 2

def parity_bit(data: int, mode: Parity) -> int:
    p = parity_xor(data)                   # =1, якщо одиниць у даних непарно
    if mode is Parity.EVEN: return p       # even: P доповнює до парного
    if mode is Parity.ODD:  return p ^ 1   # odd: дзеркально
    return 0                               # none: біта нема

# Зібрати кадр 8N1 у 16-бітне слово; нульовий біт слова виходить у лінію першим.
def build_frame_8N1(data: int) -> int:
    frame = 0
    frame |= 0 << 0                  # старт «0» (позиція 0)
    frame |= data << 1               # 8 біт даних (позиції 1..8), LSB-first задарма
    frame |= 1 << 9                  # стоп «1» (позиція 9)
    return frame                     # напр. 0x41 → 0x282
