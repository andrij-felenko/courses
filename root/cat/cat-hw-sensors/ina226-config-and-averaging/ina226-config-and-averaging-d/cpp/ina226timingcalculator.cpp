// Обчислення часу вимірювального циклу та частоти оновлення INA226
#include <array>
#include <cstdint>

class INA226TimingCalculator {
public:
    static constexpr std::array<uint32_t, 8> conv_time_us{140, 204, 332, 588, 1101, 2116, 4156, 8244};
    static constexpr std::array<uint32_t, 8> avg_samples{1, 4, 16, 64, 128, 256, 512, 1024};

    static constexpr uint32_t get_cycle_time_us(uint16_t config_reg) noexcept {
        const uint8_t avg_idx  = (config_reg >> 9) & 0x07;
        const uint8_t vbus_idx = (config_reg >> 6) & 0x07;
        const uint8_t vsh_idx  = (config_reg >> 3) & 0x07;
        const uint8_t mode     = config_reg & 0x07;

        const uint32_t t_vsh  = (mode & 0x01) ? conv_time_us[vsh_idx] : 0;
        const uint32_t t_vbus = (mode & 0x02) ? conv_time_us[vbus_idx] : 0;

        return (t_vsh + t_vbus) * avg_samples[avg_idx];
    }

    static constexpr float get_update_rate_hz(uint16_t config_reg) noexcept {
        const uint32_t cycle_us = get_cycle_time_us(config_reg);
        return (cycle_us > 0) ? (1000000.0f / static_cast<float>(cycle_us)) : 0.0f;
    }
};
