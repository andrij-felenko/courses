volatile uint8_t brightness = 4;   // 1..4: скільки підкроків із 4 рядок світить
volatile uint8_t subTick   = 0;    // 0..3: поточний підкрок усередині рядка

void scanStepPWM() {
    subTick++;
    if (subTick < 4) {
        // Ще той самий рядок; гасимо його, якщо вичерпав свою частку яскравості.
        if (subTick == brightness)
            digitalWrite(ROW_PIN[curRow], LOW);
        return;
    }
    // subTick дійшов 4 → час нового рядка.
    subTick = 0;
    digitalWrite(ROW_PIN[curRow], LOW);      // згасити старий
    curRow = (curRow + 1) & 7;
    uint8_t bits = frame[curRow];
    for (uint8_t c = 0; c < 8; c++)
        digitalWrite(COL_PIN[c], (bits & (1 << c)) ? LOW : HIGH);
    if (brightness > 0)
        digitalWrite(ROW_PIN[curRow], HIGH); // запалити новий (якщо не нульова яскравість)
}
