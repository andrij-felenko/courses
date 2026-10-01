#include <Arduino.h>
#include <Wire.h>

class ADXL345PowerManager {
private:
    static constexpr uint8_t ADXL345_ADDR = 0x53;
    static constexpr uint8_t REG_OFSX = 0x1E;
    static constexpr uint8_t REG_BW_RATE = 0x2C;
    static constexpr uint8_t REG_POWER_CTL = 0x2D;

    void writeRegister(uint8_t reg, uint8_t val) {
        Wire.beginTransmission(ADXL345_ADDR);
        Wire.write(reg);
        Wire.write(val);
        Wire.endTransmission();
    }

public:
    void enableAutoSleep() {
        // Перехід у режим очікування Standby перед конфігуруванням
        writeRegister(REG_POWER_CTL, 0x00);

        // Налаштування ODR на 100 Гц
        writeRegister(REG_BW_RATE, 0x0A);

        // Активація заповнення бітів Link(5), AutoSleep(4), Measure(3)
        writeRegister(REG_POWER_CTL, 0x38);
    }

    void setOffsetCorrection(int8_t offX, int8_t offY, int8_t offZ) {
        writeRegister(REG_OFSX, static_cast<uint8_t>(offX));
        writeRegister(REG_OFSX + 1, static_cast<uint8_t>(offY));
        writeRegister(REG_OFSX + 2, static_cast<uint8_t>(offZ));
    }
};
