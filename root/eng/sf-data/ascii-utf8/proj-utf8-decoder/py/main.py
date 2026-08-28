# повертає (код-точку, наступну позицію) або (None, позиція ресинку)
MIN_FOR_LENGTH = {1: 0x80, 2: 0x800, 3: 0x10000}

def decode_one(data, i):              # i — позиція в потоці
    b0 = data[i]
    if b0 < 0x80:                     # 0xxxxxxx — ASCII, 1 байт
        return (b0, i + 1)
    elif (b0 & 0xE0) == 0xC0:         # 110xxxxx — 2 байти
        cp, n = b0 & 0x1F, 1
    elif (b0 & 0xF0) == 0xE0:         # 1110xxxx — 3 байти
        cp, n = b0 & 0x0F, 2
    elif (b0 & 0xF8) == 0xF0:         # 11110xxx — 4 байти
        cp, n = b0 & 0x07, 3
    else:
        return (None, i + 1)          # 10xxxxxx як перший — биття/збій

    for k in range(1, n + 1):         # добираємо байти-продовження
        bk = data[i + k]
        if (bk & 0xC0) != 0x80:       # кожен мусить бути 10xxxxxx
            return (None, i + 1)      # збій — шукаємо новий старт
        cp = (cp << 6) | (bk & 0x3F)  # пришиваємо 6 біт навантаження

    if cp < MIN_FOR_LENGTH[n]:        # відкинути overlong (див. нижче)
        return (None, i + 1)
    return (cp, i + n + 1)
