#include <iostream>
#include <cmath>
#include <cstdint>
#include <expected>
#include <chrono>
#include <format>
#include <span>

namespace radio {

enum class SpreadingFactor : uint8_t {
    SF7 = 7, SF8 = 8, SF9 = 9, SF10 = 10, SF11 = 11, SF12 = 12
};

enum class BandwidthHz : uint32_t {
    BW_125kHz = 125000,
    BW_250kHz = 250000,
    BW_500kHz = 500000
};

enum class CodingRate : uint8_t {
    CR_4_5 = 1, CR_4_6 = 2, CR_4_7 = 3, CR_4_8 = 4
};

enum class ToaError {
    InvalidSpreadingFactor,
    InvalidBandwidth,
    PayloadTooLarge
};

struct LoraConfig {
    SpreadingFactor sf{SpreadingFactor::SF7};
    BandwidthHz bw{BandwidthHz::BW_125kHz};
    CodingRate cr{CodingRate::CR_4_5};
    uint16_t preamble_symbols{8};
    bool explicit_header{true};
    bool enable_crc{true};
    bool auto_ldro{true};
};

struct ToaResult {
    std::chrono::microseconds toa;
    std::chrono::microseconds required_off_time;
    uint16_t payload_symbols;

    [[nodiscard]] constexpr double toa_milliseconds() const noexcept {
        return static_cast<double>(toa.count()) / 1000.0;
    }

    [[nodiscard]] constexpr double off_time_seconds() const noexcept {
        return static_cast<double>(required_off_time.count()) / 1000000.0;
    }
};

class TimeOnAirCalculator {
public:
    [[nodiscard]] static std::expected<ToaResult, ToaError> calculate(
        const LoraConfig& config,
        std::span<const uint8_t> payload
    ) noexcept {
        if (payload.size() > 255) {
            return std::unexpected(ToaError::PayloadTooLarge);
        }

        const auto sf_val = static_cast<uint8_t>(config.sf);
        const auto bw_val = static_cast<double>(config.bw);

        if (sf_val < 7 || sf_val > 12) {
            return std::unexpected(ToaError::InvalidSpreadingFactor);
        }
        if (bw_val <= 0.0) {
            return std::unexpected(ToaError::InvalidBandwidth);
        }

        // 1. Тривалість символа у мікросекундах
        const double symbol_duration_us = (static_cast<double>(1UL << sf_val) / bw_val) * 1000000.0;

        // 2. Визначення режиму LDRO
        const bool use_ldro = config.auto_ldro && (symbol_duration_us > 16000.0);
        const uint8_t de_bit = use_ldro ? 1 : 0;

        // 3. Тривалість преамбули
        const double preamble_duration_us = (static_cast<double>(config.preamble_symbols) + 4.25) * symbol_duration_us;

        // 4. Обчислення корисного навантаження
        const auto payload_bytes = static_cast<int32_t>(payload.size());
        int32_t bits_num = 8 * payload_bytes - 4 * sf_val + 28 + (config.enable_crc ? 16 : 0) - (config.explicit_header ? 0 : 20);
        if (bits_num < 0) {
            bits_num = 0;
        }

        const int32_t bits_den = 4 * (sf_val - 2 * de_bit);
        const auto blocks = static_cast<uint16_t>(std::ceil(static_cast<double>(bits_num) / static_cast<double>(bits_den)));

        const auto cr_val = static_cast<uint8_t>(config.cr);
        const auto payload_symbols = static_cast<uint16_t>(8 + blocks * (cr_val + 4));
        const double payload_duration_us = static_cast<double>(payload_symbols) * symbol_duration_us;

        const auto total_toa_us = static_cast<uint64_t>(std::ceil(preamble_duration_us + payload_duration_us));
        const auto off_time_us = total_toa_us * 99ULL;

        return ToaResult{
            .toa = std::chrono::microseconds(total_toa_us),
            .required_off_time = std::chrono::microseconds(off_time_us),
            .payload_symbols = payload_symbols
        };
    }
};

} // namespace radio

int main() {
    using namespace radio;

    LoraConfig config{
        .sf = SpreadingFactor::SF7,
        .bw = BandwidthHz::BW_125kHz,
        .cr = CodingRate::CR_4_5,
        .preamble_symbols = 8,
        .explicit_header = true,
        .enable_crc = true,
        .auto_ldro = true
    };

    uint8_t dummy_payload[20] = {0};
    auto result = TimeOnAirCalculator::calculate(config, dummy_payload);

    if (result) {
        std::cout << std::format("SF7, BW 125 kHz, Payload 20 bytes:\n");
        std::cout << std::format("  ToA: {:.2f} ms\n", result->toa_milliseconds());
        std::cout << std::format("  Off-Time (1% DC): {:.2f} s\n", result->off_time_seconds());
        std::cout << std::format("  Payload symbols: {}\n", result->payload_symbols);
    } else {
        std::cerr << "Помилка розрахунку калькулятора ToA\n";
    }

    return 0;
}
