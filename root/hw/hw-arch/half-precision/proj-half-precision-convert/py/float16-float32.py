import struct

# float16 -> float32. Денормаль float16 стає НОРМАЛЬНИМ float32 (треба нормалізувати).
def f16_to_f32(h: int) -> float:
    sign = (h & 0x8000) << 16    # знак на місце float32
    exp  = (h >> 10) & 0x1F      # 5 бітів порядку
    mant = h & 0x03FF            # 10 бітів мантиси

    if exp == 0:                                 # порядок 0: нуль або денормаль
        if mant == 0:
            bits = sign                          # ±0
        else:
            # денормаль float16 → нормаль float32: зсуваємо мантису, доки
            # неявна одиниця (біт 0x0400) не «випливе», рахуючи зсуви в порядку.
            exp = 1
            while (mant & 0x0400) == 0:
                mant <<= 1
                exp -= 1
            mant &= 0x03FF                       # прибрати неявну одиницю
            bits = sign | ((exp - 15 + 127) << 23) | (mant << 13)
    elif exp == 0x1F:                            # порядок усі одиниці: ∞ або NaN
        bits = sign | 0x7F800000 | (mant << 13)  # мантиса 0 → ∞; ≠0 → NaN (payload зберігся)
    else:                                        # нормальне число
        bits = sign | ((exp - 15 + 127) << 23) | (mant << 13)

    return struct.unpack("<f", struct.pack("<I", bits))[0]
