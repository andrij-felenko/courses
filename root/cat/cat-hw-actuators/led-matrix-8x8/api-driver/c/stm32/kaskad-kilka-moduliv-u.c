#define N 4                       // скільки модулів у ланцюгу
uint8_t frames[N][8];             // окремий буфер на кожен модуль

// Надіслати один рядок r у ВСІ модулі за один прохід LOAD.
void chainSendRow(uint8_t r) {
    HAL_GPIO_WritePin(LOAD_PORT, LOAD_PIN, GPIO_PIN_RESET);
    // Найдальший у ланцюгу чип має отримати свій кадр ПЕРШИМ —
    // бо наступні кадри проштовхнуть його далі по ланцюгу.
    for (int8_t dev = N - 1; dev >= 0; dev--) {
        uint16_t f = ((uint16_t)(r + 1) << 8) | frames[dev][r];
        for (int8_t i = 15; i >= 0; i--) {
            HAL_GPIO_WritePin(CLK_PORT, CLK_PIN, GPIO_PIN_RESET);
            HAL_GPIO_WritePin(DIN_PORT, DIN_PIN,
                              ((f >> i) & 1) ? GPIO_PIN_SET : GPIO_PIN_RESET);
            HAL_GPIO_WritePin(CLK_PORT, CLK_PIN, GPIO_PIN_SET);
        }
    }
    HAL_GPIO_WritePin(LOAD_PORT, LOAD_PIN, GPIO_PIN_SET);  // усі чипи клацнули разом
}

// Повний кадр усього ланцюга — це вісім таких проходів.
void chainShow(void) {
    for (uint8_t r = 0; r < 8; r++)
        chainSendRow(r);
}
