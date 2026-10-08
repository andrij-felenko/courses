#include <cstdint>
#include <cstddef>
#include <span>

struct RegisterConfig {
    Ov3640SccbDriver::Bank bank;
    uint16_t reg;
    uint8_t val;
};

class Ov3640Initializer {
public:
    explicit Ov3640Initializer(Ov3640SccbDriver& driver) : driver_(driver) {}

    int checkChipId() {
        uint8_t idH = 0, idL = 0;
        if (driver_.readReg(Ov3640SccbDriver::Bank::Sensor, 0x300A, &idH) != 0) return -1;
        if (driver_.readReg(Ov3640SccbDriver::Bank::Sensor, 0x300B, &idL) != 0) return -1;
        
        uint16_t chipId = (static_cast<uint16_t>(idH) << 8) | idL;
        return (chipId == 0x3640) ? 0 : -2;
    }

    int writeTable(std::span<const RegisterConfig> table) {
        for (const auto& entry : table) {
            int res = driver_.writeReg(entry.bank, entry.reg, entry.val);
            if (res != 0) return res;
        }
        return 0;
    }

    int initialize() {
        if (driver_.writeReg(Ov3640SccbDriver::Bank::Sensor, 0x3012, 0x80) != 0) return -1;
        hardwareDelayMs(10);

        if (checkChipId() != 0) return -2;

        static constexpr RegisterConfig initArray[] = {
            {Ov3640SccbDriver::Bank::Sensor, 0x3010, 0x00},
            {Ov3640SccbDriver::Bank::Dsp,    0x3600, 0x04},
            {Ov3640SccbDriver::Bank::Dsp,    0x3601, 0x30}
        };
        return writeTable(initArray);
    }

private:
    Ov3640SccbDriver& driver_;
    extern void hardwareDelayMs(uint32_t ms);
};
