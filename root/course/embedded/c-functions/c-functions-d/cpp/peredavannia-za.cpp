struct Reading {
    float samples[64];      // 64 числа по 4 байти = 256 байтів
    uint32_t timestamp;
    uint8_t  channel;
};                          // структура ~264 байти

float average(Reading r) {  // r — КОПІЯ всіх 264 байтів!
    float sum = 0;
    for (int i = 0; i < 64; i++) sum += r.samples[i];
    return sum / 64;
}
