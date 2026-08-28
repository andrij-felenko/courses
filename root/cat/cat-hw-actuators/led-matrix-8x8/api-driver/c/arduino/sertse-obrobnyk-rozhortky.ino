volatile uint8_t curRow = 0;   // який рядок показуємо цієї ітерації

void scanStep() {
    // 1. ПОГАСИТИ попередній рядок ПЕРШИМ ділом — інакше буде перекриття.
    digitalWrite(ROW_PIN[curRow], LOW);      // закрити ключ старого рядка

    // 2. Перейти до наступного рядка по колу.
    curRow = (curRow + 1) & 7;               // 0,1,…,7,0,1,… (& 7 = % 8)

    // 3. Виставити на стовпці узор саме цього рядка.
    uint8_t bits = frame[curRow];
    for (uint8_t c = 0; c < 8; c++) {
        // спільний анод: цятка горить, коли стовпець = LOW.
        bool lit = bits & (1 << c);
        digitalWrite(COL_PIN[c], lit ? LOW : HIGH);
    }

    // 4. І аж ТЕПЕР увімкнути новий рядок.
    digitalWrite(ROW_PIN[curRow], HIGH);     // відкрити ключ → рядок світить
}
