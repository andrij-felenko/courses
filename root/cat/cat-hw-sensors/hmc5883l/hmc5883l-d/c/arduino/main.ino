#include <Wire.h>
#define HMC 0x1E   // 7-бітна I²C-адреса HMC5883L

void hmc_init() {
    Wire.begin();
    Wire.beginTransmission(HMC);
    Wire.write(0x00); Wire.write(0x70);   // Config A: 8 усереднень, 15 Гц
    Wire.endTransmission();
    Wire.beginTransmission(HMC);
    Wire.write(0x01); Wire.write(0x20);   // Config B: підсилення ±1.3 Гаус
    Wire.endTransmission();
    Wire.beginTransmission(HMC);
    Wire.write(0x02); Wire.write(0x00);   // Mode: безперервний вимір
    Wire.endTransmission();
}

void hmc_read(int16_t *x, int16_t *y, int16_t *z) {
    Wire.beginTransmission(HMC);
    Wire.write(0x03);                     // почати з першого регістра даних
    Wire.endTransmission();
    Wire.requestFrom(HMC, 6);             // 6 байтів: X, Z, Y (саме такий порядок!)
    *x = (Wire.read() << 8) | Wire.read();
    *z = (Wire.read() << 8) | Wire.read();   // Z йде ДРУГИМ, не третім
    *y = (Wire.read() << 8) | Wire.read();
}
