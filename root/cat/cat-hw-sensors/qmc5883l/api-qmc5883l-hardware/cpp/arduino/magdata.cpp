#include <Wire.h>

#define QMC5883L_ADDR 0x0D

struct MagData {
    int16_t x;
    int16_t y;
    int16_t z;
    bool overflow;
};

bool readQMC5883L(MagData &data) {
    // Читаємо Status Register (0x06)
    Wire.beginTransmission(QMC5883L_ADDR);
    Wire.write(0x06);
    if (Wire.endTransmission() != 0) return false;

    Wire.requestFrom(QMC5883L_ADDR, (uint8_t)1);
    if (!Wire.available()) return false;
    uint8_t status = Wire.read();

    if (!(status & 0x01)) return false; // DRDY == 0
    data.overflow = (status & 0x02) != 0; // Перевірка OVFL

    // Атомарне групове зчитування 6 байтів (0x00..0x05)
    Wire.beginTransmission(QMC5883L_ADDR);
    Wire.write(0x00);
    if (Wire.endTransmission() != 0) return false;

    Wire.requestFrom(QMC5883L_ADDR, (uint8_t)6);
    if (Wire.available() < 6) return false;

    uint8_t x_lsb = Wire.read();
    uint8_t x_msb = Wire.read();
    uint8_t y_lsb = Wire.read();
    uint8_t y_msb = Wire.read();
    uint8_t z_lsb = Wire.read();
    uint8_t z_msb = Wire.read();

    data.x = (int16_t)((uint16_t)x_msb << 8 | x_lsb);
    data.y = (int16_t)((uint16_t)y_msb << 8 | y_lsb);
    data.z = (int16_t)((uint16_t)z_msb << 8 | z_lsb);

    return true;
}
