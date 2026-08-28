#include <complex>
#include <cstdint>
#include <chrono>
#include <optional>

namespace rf_metrics {

using IqSample = std::complex<float>;

struct ModulationImperfections {
    double cfo_hz{0.0};
    double cfo_ppm{0.0};
    double gain_imbalance{1.0};
    double phase_skew_deg{0.0};
    std::complex<double> dc_offset{0.0, 0.0};
    double image_rejection_db{0.0};
};

struct TransientProfile {
    std::chrono::nanoseconds rise_time{0};
    double overshoot_ratio{0.0};
    std::chrono::nanoseconds settling_time{0};
};

struct SignalQuality {
    double evm_rms_percent{0.0};
    double snr_db{0.0};
    std::size_t sample_count{0};
};

struct EmitterFingerprint {
    ModulationImperfections modulation;
    TransientProfile transient;
    SignalQuality quality;
};

} // namespace rf_metrics
