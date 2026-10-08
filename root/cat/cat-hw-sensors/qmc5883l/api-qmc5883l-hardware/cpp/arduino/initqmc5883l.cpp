#include <Wire.h>
#define QMC5883L_ADDR 0x0D

bool initQMC5883L() {
    // 1. Виконання Soft Reset
    Wire.beginTransmission(QMC5883L_ADDR);
    Wire.write(0x0A);
    Wire.write(0x80);
    if (Wire.endTransmission() != 0) return false;
    delay(10);

    // 2. Налаштування періоду SET/RESET
    Wire.beginTransmission(QMC5883L_ADDR);
    Wire.write(0x0B);
    Wire.write(0x01);
    if (Wire.endTransmission() != 0) return false;

    // 3. Конфігурація: OSR=512, RNG=±8G, ODR=200Hz, Continuous Mode (0x1D)
    Wire.beginTransmission(QMC5883L_ADDR);
    Wire.write(0x09);
    Wire.write(0x1D);
    return (Wire.endTransmission() == 0);
}
