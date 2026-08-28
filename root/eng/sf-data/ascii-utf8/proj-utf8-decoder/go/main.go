// повертає код-точку, наступну позицію та ok=false на збої (позиція — ресинк)
var minForLength = [...]rune{1: 0x80, 2: 0x800, 3: 0x10000}

func decodeOne(data []byte, i int) (rune, int, bool) { // i — позиція в потоці
    b0 := data[i]
    var cp rune
    var n int
    switch {
    case b0 < 0x80: // 0xxxxxxx — ASCII, 1 байт
        return rune(b0), i + 1, true
    case b0&0xE0 == 0xC0: // 110xxxxx — 2 байти
        cp, n = rune(b0&0x1F), 1
    case b0&0xF0 == 0xE0: // 1110xxxx — 3 байти
        cp, n = rune(b0&0x0F), 2
    case b0&0xF8 == 0xF0: // 11110xxx — 4 байти
        cp, n = rune(b0&0x07), 3
    default:
        return 0, i + 1, false // 10xxxxxx як перший — биття/збій
    }

    for k := 1; k <= n; k++ { // добираємо байти-продовження
        bk := data[i+k]
        if bk&0xC0 != 0x80 { // кожен мусить бути 10xxxxxx
            return 0, i + 1, false // збій — шукаємо новий старт
        }
        cp = cp<<6 | rune(bk&0x3F) // пришиваємо 6 біт навантаження
    }

    if cp < minForLength[n] { // відкинути overlong (див. нижче)
        return 0, i + 1, false
    }
    return cp, i + n + 1, true
}
