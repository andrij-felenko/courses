// прочитати прискорення трьох осей у одиницях g; повертає код помилки
uint8_t mpu_read_accel(float *ax, float *ay, float *az) {
    uint8_t b[6];
    uint8_t err = mpu_read(REG_XOUT_H, b, 6);    // X, Y, Z — одним пакетом
    if (err) return err;
    int16_t rx = (int16_t)((b[0] << 8) | b[1]);  // старший байт ПЕРШИЙ
    int16_t ry = (int16_t)((b[2] << 8) | b[3]);
    int16_t rz = (int16_t)((b[4] << 8) | b[5]);
    const float SENS = 4096.0f;                   // ±8g → 4096 LSB/g
    *ax = rx / SENS;
    *ay = ry / SENS;
    *az = rz / SENS;
    return MPU_OK;
}
