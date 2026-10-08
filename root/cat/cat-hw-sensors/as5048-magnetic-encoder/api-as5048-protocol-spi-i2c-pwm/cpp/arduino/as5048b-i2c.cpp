#include <Wire.h>

class AS5048B_I2C {
private:
    uint8_t i2cAddr;

    uint8_t readRegister(uint8_t reg) {
        Wire.beginTransmission(i2cAddr);
        Wire.write(reg);
        Wire.endTransmission(false);
        Wire.requestFrom(i2cAddr, (uint8_t)1);
        if (Wire.available()) {
            return Wire.read();
        }
        return 0;
    }

public:
    AS5048B_I2C(uint8_t addr = 0x40) : i2cAddr(addr) {}

    void begin() {
        Wire.begin();
    }

    bool readAngle(float &angleDeg) {
        // Суворий порядок: спочатку MSB (0xFE), потім LSB (0xFF)
        uint8_t msb = readRegister(0xFE);
        uint8_t lsb = readRegister(0xFF);

        uint16_t rawAngle = ((uint16_t)msb << 6) | (lsb & 0x3F);
        angleDeg = (float)rawAngle * 360.0f / 16384.0f;
        return true;
    }
};
