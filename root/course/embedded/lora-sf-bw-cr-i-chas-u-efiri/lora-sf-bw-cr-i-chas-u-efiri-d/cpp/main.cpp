#include <cstdint>
#include <chrono>
#include <algorithm>
#include <optional>

namespace lora {

using namespace std::chrono_literals;

enum class SpreadingFactor : uint8_t {
    SF5  = 5,
    SF6  = 6,
    SF7  = 7,
    SF8  = 8,
    SF9  = 9,
    SF10 = 10,
    SF11 = 11,
    SF12 = 12
};

enum class Bandwidth : uint32_t {
    BW125 = 125000,
    BW250 = 250000,
    BW500 = 500000
};

enum class CodingRate : uint8_t {
    CR4_5 = 1,
    CR4_6 = 2,
    CR4_7 = 3,
    CR4_8 = 4
};

struct FrameConfig {
    SpreadingFactor sf{SpreadingFactor::SF7};
    Bandwidth       bw{Bandwidth::BW125};
    CodingRate      cr{CodingRate::CR4_5};
    uint16_t        preamble_len{8};
    bool            explicit_header{true};
    bool            crc_enabled{true};
    bool            low_data_rate_opt{false};
};

class AirTimeCalculator {
public:
    // Розрахунок часу в ефірі (ToA) з використанням типізованого chrono::microseconds
    static constexpr std::chrono::microseconds calculate_toa(const FrameConfig& cfg, uint8_t payload_len) noexcept {
        const auto sf_val = static_cast<uint8_t>(cfg.sf);
        const auto bw_val = static_cast<uint32_t>(cfg.bw);
        const auto cr_val = static_cast<uint8_t>(cfg.cr);

        // 1. Тривалість одного символу Ts в мікросекундах
        const uint64_t n_chips = 1ULL << sf_val;
        const auto ts_us = static_cast<uint32_t>((n_chips * 1'000'000ULL) / bw_val);

        // 2. Тривалість преамбули (N_preamble + 4.25) * Ts
        const uint32_t n_pream_x4 = (static_cast<uint32_t>(cfg.preamble_len) * 4) + 17;
        const auto t_preamble_us = static_cast<uint32_t>((static_cast<uint64_t>(n_pream_x4) * ts_us) / 4);

        // 3. Автоматичний LDRO для символів довше 16.38 мс
        const bool de_opt = cfg.low_data_rate_opt || (ts_us > 16380);
        const int32_t de_val = de_opt ? 1 : 0;
        const int32_t h_val = cfg.explicit_header ? 0 : 1;
        const int32_t crc_val = cfg.crc_enabled ? 1 : 0;

        // 4. Символи корисного навантаження
        const int32_t num = 8 * static_cast<int32_t>(payload_len) - 4 * sf_val + 28 + 16 * crc_val - 20 * h_val;
        const int32_t den = 4 * (sf_val - 2 * de_val);

        int32_t n_payload_sym = 8;
        if (num > 0 && den > 0) {
            const int32_t ceil_val = (num + den - 1) / den;
            n_payload_sym += ceil_val * (cr_val + 4);
        }

        const auto t_payload_us = static_cast<uint32_t>(n_payload_sym) * ts_us;
        return std::chrono::microseconds{t_preamble_us + t_payload_us};
    }

    // Розрахунок мінімальної паузи мовчання для заданого Duty Cycle
    static constexpr std::chrono::milliseconds calculate_time_off(std::chrono::microseconds toa, double duty_cycle_fraction = 0.01) noexcept {
        if (duty_cycle_fraction <= 0.0 || duty_cycle_fraction >= 1.0) {
            return 0ms;
        }
        const double toa_ms = static_cast<double>(toa.count()) / 1000.0;
        const double off_ms = toa_ms * ((1.0 / duty_cycle_fraction) - 1.0);
        return std::chrono::milliseconds{static_cast<int64_t>(off_ms + 0.5)};
    }

    // Підбір найефективнішого SF за виміряним SNR з урахуванням запасу затухання
    static constexpr SpreadingFactor select_sf_from_snr(int8_t snr_db, int8_t safety_margin_db = 10) noexcept {
        if (snr_db >= (-7 + safety_margin_db))  return SpreadingFactor::SF7;
        if (snr_db >= (-10 + safety_margin_db)) return SpreadingFactor::SF8;
        if (snr_db >= (-12 + safety_margin_db)) return SpreadingFactor::SF9;
        if (snr_db >= (-15 + safety_margin_db)) return SpreadingFactor::SF10;
        if (snr_db >= (-17 + safety_margin_db)) return SpreadingFactor::SF11;
        return SpreadingFactor::SF12;
    }
};

} // namespace lora
