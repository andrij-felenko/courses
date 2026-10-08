#include <Wire.h>
#include <stdint.h>

class OV2640DVPController {
private:
    static const uint8_t OV2640_I2C_ADDR = 0x30;
    static const uint8_t BANK_SEL_REG = 0xFF;
    static const uint8_t CLKRC_REG = 0x11;
    static const uint8_t COM10_REG = 0x15;

    bool writeReg(uint8_t bank, uint8_t reg, uint8_t val) {
        Wire.beginTransmission(OV2640_I2C_ADDR);
        Wire.write(BANK_SEL_REG);
        Wire.write(bank);
        if (Wire.endTransmission() != 0) return false;

        Wire.beginTransmission(OV2640_I2C_ADDR);
        Wire.write(reg);
        Wire.write(val);
        return (Wire.endTransmission() == 0);
    }

public:
    bool setupTiming(uint8_t prescaler, bool invertPclk, bool invertVsync) {
        // Запис у Bank 0 дільника частоти PCLK
        if (!writeReg(0, CLKRC_REG, prescaler & 0x3F)) return false;

        uint8_t com10 = 0;
        if (invertPclk) com10 |= (1 << 4);
        if (invertVsync) com10 |= (1 << 1);

        return writeReg(0, COM10_REG, com10);
    }
};
