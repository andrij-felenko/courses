# Наївний RLE: серію однакових байтів пишемо парою (лічильник, символ).
# Лічильник — один байт, тож серію довшу за 255 ріжемо на шматки.
# Повертає bytes із пар (лічильник, символ); у гіршому разі — 2*len(src).
def rle_encode(src: bytes) -> bytes:
    dst = bytearray()
    i, n = 0, len(src)
    while i < n:
        v = src[i]
        run = 1
        # рахуємо серію, поки той самий байт і поки влазить у лічильник 8 біт
        while i + run < n and src[i + run] == v and run < 255:
            run += 1
        dst.append(run)   # лічильник
        dst.append(v)     # символ
        i += run
    return bytes(dst)
