#include <cmath>
#include <cstdint>
#include <span>

struct DomData {
    double temp_c;
    double vcc_volts;
    double tx_bias_ma;
    double tx_power_dbm;
    double rx_power_dbm;

    static DomData parseSff8472(std::span<const uint8_t> a2_page) {
        if (a2_page.size() < 106) {
            return {};
        }

        const auto read_u16 = [&](size_t offset) -> uint16_t {
            return static_cast<uint16_t>((a2_page[offset] << 8) | a2_page[offset + 1]);
        };

        const auto read_i16 = [&](size_t offset) -> int16_t {
            return static_cast<int16_t>((a2_page[offset] << 8) | a2_page[offset + 1]);
        };

        const double tx_mw = static_cast<double>(read_u16(102)) * 0.0001;
        const double rx_mw = static_cast<double>(read_u16(104)) * 0.0001;

        return DomData{
            .temp_c = static_cast<double>(read_i16(96)) / 256.0,
            .vcc_volts = static_cast<double>(read_u16(98)) / 10000.0,
            .tx_bias_ma = static_cast<double>(read_u16(100)) * 0.002,
            .tx_power_dbm = (tx_mw > 0.0) ? 10.0 * std::log10(tx_mw) : -40.0,
            .rx_power_dbm = (rx_mw > 0.0) ? 10.0 * std::log10(rx_mw) : -40.0
        };
    }
};
