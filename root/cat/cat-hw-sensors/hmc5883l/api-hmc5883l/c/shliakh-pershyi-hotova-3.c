// Повертає true, якщо є нові валідні дані. x,y,z — сирі відліки зі знаком.
bool compass_read(int16_t *x, int16_t *y, int16_t *z) {
    uint8_t b[6];

    if (chip == CHIP_HMC) {
        // HMC: дані з 0x03, порядок у чипі X(MSB,LSB) Z(MSB,LSB) Y(MSB,LSB)
        if (reg_read(ADDR_HMC, 0x03, b, 6) != 6) return false;
        *x = (int16_t)((b[0] << 8) | b[1]);
        *z = (int16_t)((b[2] << 8) | b[3]);   // Z — ДРУГИЙ, не третій!
        *y = (int16_t)((b[4] << 8) | b[5]);   // Y — третій
        // Маркер переповнення: будь-яка вісь == -4096 → поле завелике
        if (*x == -4096 || *y == -4096 || *z == -4096) return false;
    }
    else if (chip == CHIP_QMC) {
        // QMC: дані з 0x00, порядок X Y Z, кожне число LITTLE-ENDIAN (LSB першим)
        if (reg_read(ADDR_QMC, 0x00, b, 6) != 6) return false;
        *x = (int16_t)((b[1] << 8) | b[0]);   // LSB=b[0], MSB=b[1]
        *y = (int16_t)((b[3] << 8) | b[2]);
        *z = (int16_t)((b[5] << 8) | b[4]);
    }
    else {
        return false;   // чип не знайдено
    }
    return true;
}
