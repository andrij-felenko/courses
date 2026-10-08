#include <Wire.h>
#include <stdint.h>

class OV2640BankManager {
private:
    static const uint8_t OV2640_ADDR = 0x30;
    static const uint8_t BANK_SELECT_REG = 0xFF;
    uint8_t m_activeBank;

public:
    OV2640BankManager() : m_activeBank(0xFF) {}

    bool writeRaw(uint8_t reg, uint8_t value) {
        Wire.beginTransmission(OV2640_ADDR);
        Wire.write(reg);
        Wire.write(value);
        return (Wire.endTransmission() == 0);
    }

    bool setBank(uint8_t bank) {
        if (m_activeBank == bank) return true;
        if (writeRaw(BANK_SELECT_REG, bank)) {
            m_activeBank = bank;
            return true;
        }
        return false;
    }

    bool writeRegister(uint8_t bank, uint8_t reg, uint8_t value) {
        if (!setBank(bank)) return false;
        return writeRaw(reg, value);
    }
};
