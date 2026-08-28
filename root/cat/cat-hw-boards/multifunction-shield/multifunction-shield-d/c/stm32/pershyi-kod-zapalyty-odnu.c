/* LATCH, CLK, DATA налаштовано в CubeMX як GPIO_Output (push-pull) */

// байти сегментів для цифр 0..9 (спільний анод: 0 = світиться)
static const uint8_t SEG[10] = {
    0xC0, 0xF9, 0xA4, 0xB0, 0x99, 0x92, 0x82, 0xF8, 0x80, 0x90
};
static const uint8_t SEL[4] = { 0xF1, 0xF2, 0xF4, 0xF8 };

static void ShiftOut(uint8_t b) {           // старший біт першим
    for (int i = 7; i >= 0; i--) {
        HAL_GPIO_WritePin(DATA_GPIO_Port, DATA_Pin,
                          ((b >> i) & 1) ? GPIO_PIN_SET : GPIO_PIN_RESET);
        HAL_GPIO_WritePin(CLK_GPIO_Port, CLK_Pin, GPIO_PIN_SET);   // фронт такту
        HAL_GPIO_WritePin(CLK_GPIO_Port, CLK_Pin, GPIO_PIN_RESET);
    }
}

static void ShowDigit(uint8_t value, uint8_t pos) {
    HAL_GPIO_WritePin(LATCH_GPIO_Port, LATCH_Pin, GPIO_PIN_RESET);  // набираємо
    ShiftOut(SEG[value]);       // спершу байт сегментів
    ShiftOut(SEL[pos]);         // потім байт вибору розряду
    HAL_GPIO_WritePin(LATCH_GPIO_Port, LATCH_Pin, GPIO_PIN_SET);    // клац
}

int main(void) {
    HAL_Init();
    SystemClock_Config();
    MX_GPIO_Init();
    while (1) {
        ShowDigit(5, 0);        // цифра «5» у першому (правому) розряді
        HAL_Delay(5);
    }
}
