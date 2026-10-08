#include <Wire.h>

class OV2640Driver {
public:
    static constexpr uint8_t SCCB_ADDR = 0x30;
    static constexpr uint8_t BANK_SEL  = 0xFF;
    
    enum class Bank : uint8_t {
        DSP    = 0x00,
        Sensor = 0x01
    };

    explicit OV2640Driver(TwoWire& wireBus) : bus(wireBus), activeBank(0xFF) {}

    bool setBank(Bank bank) {
        uint8_t bankValue = static_cast<uint8_t>(bank);
        if (activeBank == bankValue) {
            return true;
        }
        
        bus.beginTransmission(SCCB_ADDR);
        bus.write(BANK_SEL);
        bus.write(bankValue);
        if (bus.endTransmission() == 0) {
            activeBank = bankValue;
            return true;
        }
        return false;
    }

    bool writeRegister(Bank bank, uint8_t reg, uint8_t value) {
        if (!setBank(bank)) {
            return false;
        }
        bus.beginTransmission(SCCB_ADDR);
        bus.write(reg);
        bus.write(value);
        return (bus.endTransmission() == 0);
    }

private:
    TwoWire& bus;
    uint8_t activeBank;
};
