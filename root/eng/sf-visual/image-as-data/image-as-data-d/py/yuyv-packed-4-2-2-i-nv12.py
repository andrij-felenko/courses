# YUYV (packed 4:2:2): дістати Y,Cb,Cr для пікселя (x,y)
row  = y * stride                          # stride байтів на рядок
pair = row + (x & ~1) * 2                   # початок пари: (x/2)*4 байти
Y  = buf[pair + 2] if (x & 1) else buf[pair]   # парний → pair[0], непарний → pair[2]
Cb = buf[pair + 1]                          # спільні на пару
Cr = buf[pair + 3]

# NV12 (planar 4:2:0): дві площини в одному буфері
Yp  = 0                                     # площина Y: W*H байтів
UVp = stride * height                       # напівплощина UV одразу за Y
Y  = buf[Yp + y * stride + x]
# один відлік U/V на блок 2×2 → ділимо координати навпіл
uv = UVp + (y >> 1) * stride + (x & ~1)
Cb = buf[uv]
Cr = buf[uv + 1]
