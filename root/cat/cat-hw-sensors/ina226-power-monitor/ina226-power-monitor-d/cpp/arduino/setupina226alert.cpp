#include <Wire.h>

#define INA226_I2C_ADDR         0x40
#define INA226_REG_MASK_ENABLE   0x06
#define INA226_REG_ALERT_LIMIT   0x07

// Конфігурація апаратного Alert на платах Arduino / ESP32
void setupINA226Alert(uint16_t alertLimitCode) {
    // 1. Запис порогу в Alert Limit Register
    Wire.beginTransmission(INA226_I2C_ADDR);
    Wire.write(INA226_REG_ALERT_LIMIT);
    Wire.write((uint8_t)(alertLimitCode >> 8));
    Wire.write((uint8_t)(alertLimitCode & 0xFF));
    Wire.endTransmission();

    // 2. Ввімкнення прапорця SOL (біт 15) та защіпки Latch Enable (біт 0)
    uint16_t maskVal = (1 << 15) | (1 << 0);
    Wire.beginTransmission(INA226_I2C_ADDR);
    Wire.write(INA226_REG_MASK_ENABLE);
    Wire.write((uint8_t)(maskVal >> 8));
    Wire.write((uint8_t)(maskVal & 0xFF));
    Wire.endTransmission();
}
