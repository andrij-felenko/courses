#include <cstdint>
#include <system_error>

class Ov3640SccbDriver {
public:
    static constexpr uint8_t kSccbAddress = 0x78;
    static constexpr uint16_t kBankSelectReg = 0x3000;
    
    enum class Bank : uint8_t {
        Dsp = 0x00,
        Sensor = 0x01,
        Unknown = 0xFF
    };

    int setBank(Bank bank) {
        if (currentBank_ == bank) {
            return 0;
        }
        int res = sccbPhysicalWrite(kSccbAddress, kBankSelectReg, static_cast<uint8_t>(bank));
        if (res == 0) {
            currentBank_ = bank;
        }
        return res;
    }

    int writeReg(Bank bank, uint16_t reg, uint8_t val) {
        int res = setBank(bank);
        if (res != 0) return res;
        return sccbPhysicalWrite(kSccbAddress, reg, val);
    }

    int readReg(Bank bank, uint16_t reg, uint8_t *val) {
        int res = setBank(bank);
        if (res != 0) return res;
        return sccbPhysicalRead(kSccbAddress, reg, val);
    }

private:
    Bank currentBank_{Bank::Unknown};

    // Фізичний виклик апаратного I2C/SCCB адаптера
    extern int sccbPhysicalWrite(uint8_t dev, uint16_t reg, uint8_t val);
    extern int sccbPhysicalRead(uint8_t dev, uint16_t reg, uint8_t *val);
};
