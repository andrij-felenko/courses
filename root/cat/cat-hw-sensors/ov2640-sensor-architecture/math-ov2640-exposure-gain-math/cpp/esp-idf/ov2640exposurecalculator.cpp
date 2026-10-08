#include <cstdint>
#include <algorithm>

class OV2640ExposureCalculator {
public:
    struct RegisterConfig {
        uint8_t reg04;
        uint8_t aec;
        uint16_t dummy_lines;
    };

    static RegisterConfig compute(uint32_t target_exp_us, uint32_t f_pclk_hz,
                                 uint16_t n_pixel, uint16_t n_line) {
        RegisterConfig config{};
        if (f_pclk_hz == 0 || n_pixel == 0) return config;

        double t_line_us = (double)n_pixel * 1000000.0 / (double)f_pclk_hz;
        uint32_t aec_lines = static_cast<uint32_t>(target_exp_us / t_line_us);

        uint16_t max_standard = (n_line > 16) ? (n_line - 16) : n_line;
        if (aec_lines > max_standard) {
            config.dummy_lines = static_cast<uint16_t>(aec_lines - max_standard);
        } else {
            config.dummy_lines = 0;
        }

        uint8_t aec_1_0 = aec_lines & 0x03;
        uint8_t aec_9_2 = (aec_lines >> 2) & 0xFF;
        uint8_t aec_15_10 = (aec_lines >> 10) & 0x3F;

        config.reg04 = static_cast<uint8_t>((aec_15_10 << 2) | aec_1_0);
        config.aec = aec_9_2;

        return config;
    }
};
