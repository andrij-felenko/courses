#include <cmath>
#include <cstdint>
#include <algorithm>

namespace LoRaMath {

struct Sx1262Config {
    uint8_t sf;             // Фактор розширення (7..12)
    double bw_hz;           // Ширина смуги в Гц (наприклад, 125000.0)
    uint8_t cr;             // Код кодування (1 для 4/5, 2 для 4/6, 3 для 4/7, 4 для 4/8)
    uint8_t payload_len;    // Довжина навантаження у байтах
    uint16_t preamble_len; // Базова довжина преамбули в символах
    bool explicit_header;  // Явний заголовок кадру
    bool crc_on;           // Наявність контрольної суми CRC
};

class TimeOnAirCalculator {
public:
    static double calculateToaMs(const Sx1262Config& config) {
        const double t_s = std::pow(2.0, config.sf) / config.bw_hz;
        const bool low_dr_opt = (t_s > 0.016);
        
        const double n_preamble = static_cast<double>(config.preamble_len) + 4.25;
        const double t_preamble = n_preamble * t_s;
        
        const double h = config.explicit_header ? 0.0 : 1.0;
        const double crc = config.crc_on ? 1.0 : 0.0;
        const double de = low_dr_opt ? 1.0 : 0.0;
        
        const double num = 8.0 * config.payload_len - 4.0 * config.sf + 28.0 + 16.0 * crc - 20.0 * h;
        const double den = 4.0 * (config.sf - 2.0 * de);
        
        const double symbol_blocks = std::max(0.0, std::ceil(num / den));
        const double n_payload = 8.0 + symbol_blocks * (static_cast<double>(config.cr) + 4.0);
        const double t_payload = n_payload * t_s;
        
        return (t_preamble + t_payload) * 1000.0;
    }
};

} // namespace LoRaMath
