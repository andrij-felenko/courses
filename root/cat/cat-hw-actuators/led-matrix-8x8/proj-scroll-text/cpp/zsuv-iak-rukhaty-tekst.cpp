const char* message = "HELLO ";     // що біжить
uint8_t colBuf[8];                  // вісім видимих стовпців (буфер по стовпцях)

// Індекс символу в таблиці FONT за його кодом (тут — латиниця й пробіл).
uint8_t glyphIndex(char ch) {
    if (ch == ' ') return 0;
    if (ch >= 'A' && ch <= 'Z') return 1 + (ch - 'A');   // 'A' → 1, 'B' → 2, …
    return 0;                                            // невідоме → пробіл
}

// Обчислити вісім видимих стовпців, коли віконце зсунуте на offset стовпців.
void renderWindow(uint16_t offset) {
    uint8_t len = strlen(message);
    const uint8_t GLYPH_W = 8;                 // ширина символу в стовпцях
    for (uint8_t screenCol = 0; screenCol < 8; screenCol++) {
        uint16_t x = offset + screenCol;       // глобальний номер стовпця стрічки
        uint8_t  charPos = x / GLYPH_W;        // котрий це символ повідомлення
        uint8_t  inChar  = x % GLYPH_W;        // котрий стовпчик усередині символу
        if (charPos >= len) {                  // за кінцем тексту — порожньо
            colBuf[screenCol] = 0x00;
            continue;
        }
        uint8_t idx = glyphIndex(message[charPos]);
        colBuf[screenCol] = fontColumn(idx, inChar);   // стовпець зі шрифту (Flash)
    }
}
