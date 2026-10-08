// Формування маски конфігурації INA219 мовою C++ (Arduino / C++17)
#include <cstdint>

class Ina219ConfigBuilder {
public:
    enum class BusRange : uint16_t { Range_16V = 0, Range_32V = (1U << 13) };
    enum class PgaGain  : uint16_t { Gain_40mV = 0, Gain_80mV = (1U << 11), Gain_160mV = (2U << 11), Gain_320mV = (3U << 11) };
    enum class Mode     : uint16_t { PowerDown = 0, Triggered = 3, Continuous = 7 };

    static constexpr uint16_t makeConfig(BusRange range, PgaGain gain, uint8_t badc, uint8_t sadc, Mode mode) {
        return static_cast<uint16_t>(range) |
               static_cast<uint16_t>(gain) |
               ((static_cast<uint16_t>(badc) & 0x0FU) << 7) |
               ((static_cast<uint16_t>(sadc) & 0x0FU) << 3) |
               (static_cast<uint16_t>(mode) & 0x07U);
    }
};
