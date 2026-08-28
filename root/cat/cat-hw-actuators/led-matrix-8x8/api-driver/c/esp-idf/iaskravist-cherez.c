static volatile uint8_t brightness = 4;  // 1..4: скільки підкроків із 4 рядок світить
static volatile uint8_t subTick    = 0;  // 0..3: поточний підкрок усередині рядка

static void IRAM_ATTR scanStepPWM(void) {
    subTick++;
    if (subTick < 4) {
        // Ще той самий рядок; гасимо його, якщо вичерпав свою частку яскравості.
        if (subTick == brightness)
            gpio_set_level(ROW_PIN[curRow], 0);
        return;
    }
    // subTick дійшов 4 → час нового рядка.
    subTick = 0;
    gpio_set_level(ROW_PIN[curRow], 0);      // згасити старий
    curRow = (curRow + 1) & 7;
    uint8_t bits = frame[curRow];
    for (int c = 0; c < 8; c++)
        gpio_set_level(COL_PIN[c], (bits & (1 << c)) ? 0 : 1);
    if (brightness > 0)
        gpio_set_level(ROW_PIN[curRow], 1);  // запалити новий (якщо не нульова яскравість)
}
