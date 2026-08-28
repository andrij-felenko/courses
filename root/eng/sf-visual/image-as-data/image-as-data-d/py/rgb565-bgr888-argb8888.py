# RGB565: дістати канали з 16-бітного слова
px = int.from_bytes(buf[y*stride + x*2 : y*stride + x*2 + 2], "little")
r = (px >> 11) & 0x1F    # 5 біт  → 0..31
g = (px >>  5) & 0x3F    # 6 біт  → 0..63
b =  px        & 0x1F    # 5 біт  → 0..31

# BGR888: три байти, увага на порядок
p = y*stride + x*3
b, g, r = buf[p], buf[p+1], buf[p+2]     # ← B перший!

# ARGB8888: чотири байти
p = y*stride + (x << 2)
a, r, g, b = buf[p], buf[p+1], buf[p+2], buf[p+3]
