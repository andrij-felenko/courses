volatile uint8_t brightness = 4;   // 1..4: скільки підкроків із 4 рядок світить
volatile uint8_t subTick   = 0;    // 0..3: поточний підкрок усередині рядка

void scanStepPWM(void) {
    subTick++;
    if (subTick < 4) {
        // Ще той самий рядок; гасимо його, якщо вичерпав свою частку яскравості.
        if (subTick == brightness)
            HAL_GPIO_WritePin(ROW_PIN[curRow].port, ROW_PIN[curRow].pin, GPIO_PIN_RESET);
        return;
    }
    // subTick дійшов 4 → час нового рядка.
    subTick = 0;
    HAL_GPIO_WritePin(ROW_PIN[curRow].port, ROW_PIN[curRow].pin, GPIO_PIN_RESET);
    curRow = (curRow + 1) & 7;
    uint8_t bits = frame[curRow];
    for (uint8_t c = 0; c < 8; c++)
        HAL_GPIO_WritePin(COL_PIN[c].port, COL_PIN[c].pin,
                          (bits & (1 << c)) ? GPIO_PIN_RESET : GPIO_PIN_SET);
    if (brightness > 0)
        HAL_GPIO_WritePin(ROW_PIN[curRow].port, ROW_PIN[curRow].pin, GPIO_PIN_SET);
}
