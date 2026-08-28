#include <Wire.h>

#define MPU_ADDR     0x68
#define REG_WHO      0x75
#define REG_PWR      0x6B
#define REG_CFG      0x1C
#define REG_XOUT_H   0x3B
#define MPU_OK       0

// записати один байт val у регістр reg; повертає код помилки Wire (0 — успіх)
uint8_t mpu_write(uint8_t reg, uint8_t val) {
    Wire.beginTransmission(MPU_ADDR);
    Wire.write(reg);
    Wire.write(val);
    return Wire.endTransmission();          // 0 — успіх, інакше код збою
}

// прочитати n байтів поспіль від reg у buf; повертає код помилки
uint8_t mpu_read(uint8_t reg, uint8_t *buf, uint8_t n) {
    Wire.beginTransmission(MPU_ADDR);
    Wire.write(reg);
    uint8_t err = Wire.endTransmission(false);   // повторний старт, без stop
    if (err) return err;                         // адреса не підтвердилась — далі марно
    uint8_t got = Wire.requestFrom(MPU_ADDR, n);
    if (got != n) return 0xFF;                   // прийшло менше, ніж просили
    for (uint8_t i = 0; i < n; i++) buf[i] = Wire.read();
    return MPU_OK;
}
