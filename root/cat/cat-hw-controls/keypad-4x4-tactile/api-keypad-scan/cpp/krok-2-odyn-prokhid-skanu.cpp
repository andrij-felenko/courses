// Прочитати весь стан клавіатури в бітову карту 4×4.
// Повертає 16 бітів: біт (row*4 + col) = 1, якщо кнопка (row,col) натиснута.
static uint16_t keypad_scan_raw(void)
{
    uint16_t bits = 0;

    for (uint8_t col = 0; col < 4; col++) {
        digitalWrite(COL_PIN[col], LOW);        // 1) активуємо стовпець: тягнемо до землі
        // тут корисна крихітна пауза — див. пастку «повільний loop / надто швидкий скан»
        for (uint8_t row = 0; row < 4; row++) { // 2) читаємо всі рядки
            if (digitalRead(ROW_PIN[row]) == LOW)   // рядок просів → кнопка натиснута
                bits |= (uint16_t)1 << (row * 4 + col);
        }
        digitalWrite(COL_PIN[col], HIGH);       // 3) відпускаємо стовпець назад у HIGH
    }
    return bits;
}
