import struct

# Дістати з float три поля IEEE 754 single і зібрати значення назад.
def decode_f32(x):
    # біти float32 як ціле — без UB (пакування в 4 байти)
    bits = struct.unpack("<I", struct.pack("<f", x))[0]

    s    =  bits >> 31          # 1 біт знаку (позиція 31)
    exp  = (bits >> 23) & 0xFF  # 8 бітів порядку (30..23)
    mant =  bits & 0x7FFFFF     # 23 біти мантиси (22..0)

    # −3.5 → s = 1, exp = 128, mant = 0x600000 (двійкове 110...0)
    sign = -1.0 if s else 1.0
    frac = 1.0 + mant / 0x800000   # прихована 1 + дріб/2^23
    return sign * frac * 2.0 ** (exp - 127)   # × 2^(exp−127)
