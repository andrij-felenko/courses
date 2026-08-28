// Кодує один 14-бітний лінійний відлік у 8-бітний код μ-law.
uint8_t ulaw_encode(int16_t sample) {
    int32_t sign = 0;
    int32_t mag  = sample;
    if (mag < 0) { sign = 0x80; mag = -mag; }   // знак окремо, далі — модуль
    if (mag > 32635) mag = 32635;               // обрізаємо в межу μ-law
    mag += 0x84;                                // той самий п'єдестал (bias)

    // сегмент = позиція старшого біта величини (цілочисловий log2):
    // це і є "у яку хорду драбини лягає відлік"
    int32_t exponent = 7;
    for (int32_t mask = 0x4000; (mag & mask) == 0 && exponent > 0; mask >>= 1)
        exponent--;

    int32_t mantissa = (mag >> (exponent + 3)) & 0x0f;   // 4 біти всередині сегмента
    uint8_t code = (uint8_t)(sign | (exponent << 4) | mantissa);
    return ~code;                               // стандарт зберігає інвертованим
}
