#include <vector>
#include <complex>
#include <cmath>
#include <numbers>
#include <span>
#include <expected>
#include <numeric>

namespace rf_security {

struct EmitterMetrics {
    double cfo_hz{0.0};
    double gain_imbalance{1.0};
    double phase_skew_deg{0.0};
    std::complex<double> dc_offset{0.0, 0.0};
    double snr_db{0.0};
};

enum class AnalysisStatus {
    InvalidData,
    BufferTooShort
};

class SignatureAnalyzer {
public:
    [[nodiscard]] static std::expected<EmitterMetrics, AnalysisStatus>
    analyze(std::span<const std::complex<float>> samples, double sample_rate_hz) noexcept {
        if (samples.size() < 64) {
            return std::unexpected(AnalysisStatus::BufferTooShort);
        }

        const auto count = static_cast<double>(samples.size());

        // 1. Обчислення постійного зміщення
        const auto sum = std::accumulate(samples.begin(), samples.end(), std::complex<double>{0.0, 0.0});
        const auto dc = sum / count;

        // 2. Оцінка квадратурного дисбалансу
        double p_i = 0.0;
        double p_q = 0.0;
        double cross_iq = 0.0;

        for (const auto& s : samples) {
            const double ci = static_cast<double>(s.real()) - dc.real();
            const double cq = static_cast<double>(s.imag()) - dc.imag();
            p_i += ci * ci;
            p_q += cq * cq;
            cross_iq += ci * cq;
        }

        p_i /= count;
        p_q /= count;
        cross_iq /= count;

        const double gain_imb = (p_q > 1e-12) ? std::sqrt(p_i / p_q) : 1.0;
        const double denom = std::sqrt(p_i * p_q);
        double phase_skew_deg = 0.0;

        if (denom > 1e-12) {
            const double sin_phi = std::clamp(cross_iq / denom, -1.0, 1.0);
            phase_skew_deg = std::asin(sin_phi) * (180.0 / std::numbers::pi);
        }

        // 3. Зсув несучої частоти (CFO)
        std::complex<double> corr{0.0, 0.0};
        for (std::size_t k = 0; k < samples.size() - 1; ++k) {
            const std::complex<double> s1{samples[k + 1].real(), samples[k + 1].imag()};
            const std::complex<double> s0{samples[k].real(), samples[k].imag()};
            corr += s1 * std::conj(s0);
        }

        const double phase_diff = std::arg(corr);
        const double cfo = (phase_diff * sample_rate_hz) / (2.0 * std::numbers::pi);
        const double snr = 10.0 * std::log10((p_i + p_q) + 1e-12);

        return EmitterMetrics{
            .cfo_hz = cfo,
            .gain_imbalance = gain_imb,
            .phase_skew_deg = phase_skew_deg,
            .dc_offset = dc,
            .snr_db = snr
        };
    }
};

} // namespace rf_security
