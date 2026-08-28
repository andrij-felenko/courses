// повертає код-точку, наступну позицію та ok=false на збої (позиція — ресинк)
struct Decoded { uint32_t cp; size_t next; bool ok; };

Decoded decode_one(const uint8_t *bytes, size_t i) { // i — позиція в потоці
    static const uint32_t min_for_length[] = {0, 0x80, 0x800, 0x10000};
    uint8_t b0 = bytes[i];
    uint32_t cp;
    int n;
    if (b0 < 0x80) {                    // 0xxxxxxx — ASCII, 1 байт
        return {b0, i + 1, true};
    } else if ((b0 & 0xE0) == 0xC0) {   // 110xxxxx — 2 байти
        cp = b0 & 0x1F;  n = 1;
    } else if ((b0 & 0xF0) == 0xE0) {   // 1110xxxx — 3 байти
        cp = b0 & 0x0F;  n = 2;
    } else if ((b0 & 0xF8) == 0xF0) {   // 11110xxx — 4 байти
        cp = b0 & 0x07;  n = 3;
    } else {
        return {0, i + 1, false};       // 10xxxxxx як перший — биття/збій
    }

    for (int k = 1; k <= n; ++k) {      // добираємо байти-продовження
        uint8_t bk = bytes[i + k];
        if ((bk & 0xC0) != 0x80)        // кожен мусить бути 10xxxxxx
            return {0, i + 1, false};   // збій — шукаємо новий старт
        cp = (cp << 6) | (bk & 0x3F);   // пришиваємо 6 біт навантаження
    }

    if (cp < min_for_length[n])         // відкинути overlong (див. нижче)
        return {0, i + 1, false};
    return {cp, i + n + 1, true};
}
