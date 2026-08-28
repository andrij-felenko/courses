import math
import struct

def bits_as_int(f):                     # біти float32 як 32-бітне ціле зі знаком
    return struct.unpack("<i", struct.pack("<f", f))[0]

def near_equal_ulp(a, b, max_ulps):
    if math.isnan(a) or math.isnan(b):  # NaN не рівний нічому, навіть собі
        return False
    ia = bits_as_int(a)                 # біти float як 32-бітне ціле
    ib = bits_as_int(b)
    if (ia < 0) != (ib < 0):            # різні знаки (різні півпрямі):
        return a == b                   #   єдиний «рівний» випадок тут — ±0
    return abs(ia - ib) <= max_ulps     # та сама півпряма — рахуємо крок
