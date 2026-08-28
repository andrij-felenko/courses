const uint8_t N = 4;              // скільки модулів у ланцюгу
uint8_t frames[N][8];             // окремий буфер на кожен модуль

// Надіслати один рядок r у ВСІ модулі за один прохід LOAD.
void chainSendRow(uint8_t r) {
    digitalWrite(PIN_LOAD, LOW);
    // Найдальший у ланцюгу чип має отримати свій кадр ПЕРШИМ —
    // бо наступні кадри проштовхнуть його далі по ланцюгу.
    for (int8_t dev = N - 1; dev >= 0; dev--) {
        uint16_t f = ((uint16_t)(r + 1) << 8) | frames[dev][r];
        for (int8_t i = 15; i >= 0; i--) {
            digitalWrite(PIN_CLK, LOW);
            digitalWrite(PIN_DIN, (f >> i) & 1);
            digitalWrite(PIN_CLK, HIGH);
        }
    }
    digitalWrite(PIN_LOAD, HIGH);   // усі чипи разом клацнули свій рядок
}

// Повний кадр усього ланцюга — це вісім таких проходів.
void chainShow() {
    for (uint8_t r = 0; r < 8; r++)
        chainSendRow(r);
}
