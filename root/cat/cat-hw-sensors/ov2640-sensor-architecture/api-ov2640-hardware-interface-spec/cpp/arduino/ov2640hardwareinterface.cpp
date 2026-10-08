#include <cstdint>

class OV2640HardwareInterface {
public:
    enum class Bank : uint8_t {
        DSP     = 0x00,
        Sensor  = 0x01,
        Unknown = 0xFF
    };

    explicit OV2640HardwareInterface(uint8_t sccb_address = 0x30)
        : device_address_(sccb_address), active_bank_(Bank::Unknown) {}

    bool setBank(Bank bank) {
        if (active_bank_ == bank) {
            return true;
        }
        if (rawWrite(0xFF, static_cast<uint8_t>(bank))) {
            active_bank_ = bank;
            return true;
        }
        return false;
    }

    bool writeRegister(Bank bank, uint8_t reg, uint8_t value) {
        if (!setBank(bank)) {
            return false;
        }
        return rawWrite(reg, value);
    }

private:
    uint8_t device_address_;
    Bank active_bank_;

    bool rawWrite(uint8_t reg, uint8_t value);
};
