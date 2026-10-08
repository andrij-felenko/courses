#include <Wire.h>

const uint8_t OV2640_ADDR = 0x30;
const uint8_t BANK_SELECT_REGISTER = 0xFF;

class OV2640BankController {
public:
    static bool writeRegister(uint8_t reg, uint8_t value) {
        Wire.beginTransmission(OV2640_ADDR);
        Wire.write(reg);
        Wire.write(value);
        return (Wire.endTransmission() == 0);
    }

    static bool setBank(uint8_t bankNumber) {
        // bankNumber: 0x00 для Bank 0, 0x01 для Bank 1
        return writeRegister(BANK_SELECT_REGISTER, bankNumber);
    }
};
