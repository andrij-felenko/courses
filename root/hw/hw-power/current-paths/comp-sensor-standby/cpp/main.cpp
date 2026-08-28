#include <Wire.h>

constexpr uint8_t BME280_ADDR   = 0x76;  // або 0x77 (ADR=1)
constexpr uint8_t LIS3DH_ADDR   = 0x18;  // або 0x19 (SA0=1)
constexpr uint8_t BME_CTRL_MEAS = 0xF4;  // mode[1:0] → 00 = sleep
constexpr uint8_t LIS_CTRL_REG1 = 0x20;  // ODR[3:0]=0000 → power-down

void i2cWrite8(uint8_t addr, uint8_t reg, uint8_t val) {
    Wire.beginTransmission(addr);
    Wire.write(reg); Wire.write(val);
    Wire.endTransmission();
}

void sensorsSleep() {
    i2cWrite8(BME280_ADDR, BME_CTRL_MEAS, 0x00);  // BME → sleep
    i2cWrite8(LIS3DH_ADDR, LIS_CTRL_REG1, 0x00);  // LIS → power-down
    // esp_deep_sleep_start();  // далі — у deep-sleep
}
