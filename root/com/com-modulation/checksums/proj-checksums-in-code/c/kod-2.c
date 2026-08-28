uint16_t fletcher16(const uint8_t *data, size_t len) {
    uint16_t sum1 = 0, sum2 = 0;

    for (size_t i = 0; i < len; i++) {
        sum1 += data[i];
        if (sum1 >= 255) sum1 -= 255;   // sum1 за модулем 255 — без ділення
        sum2 += sum1;
        if (sum2 >= 255) sum2 -= 255;   // sum2 за модулем 255
    }
    return (uint16_t)((sum2 << 8) | sum1);
}
