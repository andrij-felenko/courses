#define N 4                       // скільки модулів у ланцюгу
static uint8_t frames[N][8];      // окремий буфер на кожен модуль

// Надіслати один рядок r у ВСІ модулі за один прохід LOAD.
static void chainSendRow(uint8_t r) {
    gpio_set_level(PIN_LOAD, 0);
    // Найдальший у ланцюгу чип має отримати свій кадр ПЕРШИМ —
    // бо наступні кадри проштовхнуть його далі по ланцюгу.
    for (int dev = N - 1; dev >= 0; dev--) {
        uint16_t f = ((uint16_t)(r + 1) << 8) | frames[dev][r];
        for (int i = 15; i >= 0; i--) {
            gpio_set_level(PIN_CLK, 0);
            gpio_set_level(PIN_DIN, (f >> i) & 1);
            gpio_set_level(PIN_CLK, 1);
        }
    }
    gpio_set_level(PIN_LOAD, 1);    // усі чипи разом клацнули свій рядок
}

// Повний кадр усього ланцюга — це вісім таких проходів.
static void chainShow(void) {
    for (uint8_t r = 0; r < 8; r++)
        chainSendRow(r);
}
