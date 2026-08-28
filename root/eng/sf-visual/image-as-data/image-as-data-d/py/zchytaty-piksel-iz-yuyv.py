def clamp_u8(v):
    return 0 if v < 0 else (255 if v > 255 else v)

# Зчитати піксель (x,y) з YUYV-буфера й повернути RGB888 (BT.601, limited range).
def yuyv_pixel_to_rgb(buf, stride, x, y):
    row  = y * stride
    pair = row + (x & ~1) * 2         # початок пари пікселів
    Y  = buf[pair + 2] if (x & 1) else buf[pair]   # свій Y на піксель
    Cb = buf[pair + 1]                # спільні на пару
    Cr = buf[pair + 3]

    c = 298 * (Y - 16)     # та сама цілочисельна BT.601-матриця
    d = Cb - 128
    e = Cr - 128
    r = clamp_u8((c + 409 * e           + 128) >> 8)
    g = clamp_u8((c - 100 * d - 208 * e + 128) >> 8)
    b = clamp_u8((c + 516 * d           + 128) >> 8)
    return r, g, b
