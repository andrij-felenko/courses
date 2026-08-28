#include <cstdint>
#include <chrono>

namespace rf_metrics {

enum class StealthMode : std::uint8_t {
    Burst = 0,
    Dsss = 1,
    Fhss = 2,
    Hybrid = 3
};

struct DsssParams {
    std::uint16_t spreading_factor{64};
    std::uint64_t pn_polynomial{0x800000000000000DULL};
};

struct FhssParams {
    std::uint32_t hop_rate_hz{1000};
    std::uint16_t channel_count{256};
};

struct StealthConfig {
    StealthMode mode{StealthMode::Burst};
    double tx_power_dbm{0.0};
    std::chrono::microseconds burst_duration{500};
    std::chrono::milliseconds min_silence_interval{1000};
    std::chrono::milliseconds max_silence_interval{5000};
    DsssParams dsss;
    FhssParams fhss;
};

} // namespace rf_metrics
