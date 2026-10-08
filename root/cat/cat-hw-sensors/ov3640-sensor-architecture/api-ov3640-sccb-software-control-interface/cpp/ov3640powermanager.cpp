#include <cstdint>
#include <system_error>

class Ov3640PowerManager {
public:
    explicit Ov3640PowerManager(Ov3640SccbDriver& driver) : driver_(driver) {}

    std::error_code setPowerdown(bool enable) {
        uint8_t val = enable ? 0x80 : 0x00;
        int res = driver_.writeReg(Ov3640SccbDriver::Bank::Sensor, 0x3008, val);
        if (res != 0) {
            return std::make_error_code(std::errc::io_error);
        }
        if (!enable) {
            delayMs(5);
        }
        return {};
    }

    std::error_code safeWriteWithRetry(Ov3640SccbDriver::Bank bank, uint16_t reg, uint8_t val) {
        for (int i = 0; i < 3; ++i) {
            int res = driver_.writeReg(bank, reg, val);
            if (res == 0) return {};
            if (res == -110) return std::make_error_code(std::errc::timed_out);
        }
        return std::make_error_code(std::errc::io_error);
    }

private:
    Ov3640SccbDriver& driver_;
    extern void delayMs(uint32_t ms);
};
