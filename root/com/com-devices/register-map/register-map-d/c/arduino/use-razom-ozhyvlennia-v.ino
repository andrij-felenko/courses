#include <Wire.h>

// --- адреси з даташита MPU-6050 ---
const uint8_t ADDR        = 0x68;   // адреса чіпа на шині I2C
const uint8_t REG_WHO     = 0x75;   // WHO_AM_I
const uint8_t EXPECTED_ID = 0x68;   // сталий код саме цього чіпа
const uint8_t REG_PWR     = 0x6B;   // PWR_MGMT_1
const uint8_t REG_CFG     = 0x1C;   // ACCEL_CONFIG (діапазон у бітах 4:3)
const uint8_t REG_XOUT_H  = 0x3B;   // старший байт виміру осі X

// прочитати один байт регістра reg
uint8_t readReg(uint8_t reg) {
    Wire.beginTransmission(ADDR);
    Wire.write(reg);                 // назвати номер регістра…
    Wire.endTransmission(false);     // …і ПОВТОРНИЙ старт (без stop)
    Wire.requestFrom(ADDR, (uint8_t)1);
    return Wire.read();
}

// записати один байт val у регістр reg
void writeReg(uint8_t reg, uint8_t val) {
    Wire.beginTransmission(ADDR);
    Wire.write(reg);
    Wire.write(val);
    Wire.endTransmission();
}
