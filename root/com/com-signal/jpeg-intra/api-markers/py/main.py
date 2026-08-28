def walk_jpeg(buf: bytes) -> None:
    """Пройти сегменти JPEG і надрукувати структуру файлу."""
    i, n = 0, len(buf)
    while i + 1 < n:
        if buf[i] != 0xFF:                    # маркер починається на 0xFF
            i += 1; continue
        m = buf[i + 1]
        if m == 0xFF:                         # 0xFF-заповнювач — пропустити
            i += 1; continue
        i += 2                                # проковтнули «FF xx»

        if m == 0xD8:                         # SOI — стандалон
            print("SOI"); continue
        if m == 0xD9:                         # EOI — стандалон, кінець
            print("EOI"); break
        if 0xD0 <= m <= 0xD7:                 # RST0..RST7 — стандалон
            print(f"RST{m - 0xD0}"); continue

        length = (buf[i] << 8) | buf[i + 1]   # big-endian; рахує себе + дані
        print(f"FF{m:02X}  довжина={length}  даних={length - 2}")

        if m == 0xDA:                         # SOS: далі — стиснутий потік
            i += length                       # перескочити заголовок скану…
            while i + 1 < n:                  # …і сам потік до наступного маркера
                if buf[i] == 0xFF and buf[i + 1] != 0x00 \
                        and not (0xD0 <= buf[i + 1] <= 0xD7):
                    break                     # справжній маркер (не FF00, не RSTn)
                i += 1
            continue
        i += length                           # на наступний сегмент

# walk_jpeg(open("photo.jpg", "rb").read())
