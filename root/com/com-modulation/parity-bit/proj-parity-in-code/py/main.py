from enum import Enum

# 1 — якщо серед одиниць байта непарне число (XOR усіх бітів)
def parity_of(b):
    b ^= b >> 4
    b ^= b >> 2
    b ^= b >> 1
    return b & 1

class ParityMode(Enum):
    EVEN = 0
    ODD = 1

# Пакуємо 7 біт даних (0..0x7F) + біт парності у старший (8-й) розряд.
# even: загальна кількість одиниць у байті парна; odd: непарна.
def parity_encode(data7, mode):
    p = parity_of(data7 & 0x7F)             # парність самих даних
    if mode == ParityMode.ODD:
        p ^= 1                              # для odd інвертуємо домовленість
    return (p << 7) | (data7 & 0x7F)

# True — слово ціле за обраною домовленістю; False — помилка виявлена.
def parity_check(word, mode):
    ones_odd = parity_of(word)              # парність усіх 8 бітів разом
    # even-домовленість вимагає парної суми (ones_odd == 0);
    # odd-домовленість вимагає непарної (ones_odd == 1).
    return ones_odd == (1 if mode == ParityMode.ODD else 0)
