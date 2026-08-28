#include <iostream>
#include <vector>
#include <complex>
#include <cmath>
#include <numbers>
#include <span>
#include <expected>
#include <numeric>

namespace rf {

inline constexpr double SpeedOfLight = 299792458.0;

struct Signature {
    double cfo_hz{0.0};
    double iq_gain_imbalance{1.0};
    double iq_phase_skew_deg{0.0};
    std::complex<double> dc_offset{0.0, 0.0};
    double snr_db{0.0};
};

struct Point2D {
    double x{0.0};
    double y{0.0};
};

struct TdoaSensor {
    Point2D pos;
    double timestamp_s{0.0};
};

enum class AnalysisError {
    InsufficientSamples,
    CollinearSensors,
    NonConvergent
};

class FingerprintAnalyzer {
public:
    [[nodiscard]] static std::expected<Signature, AnalysisError>
    extract(std::span<const std::complex<double>> samples, double sample_rate_hz) noexcept {
        if (samples.size() < 32) {
            return std::unexpected(AnalysisError::InsufficientSamples);
        }

        const auto count = static_cast<double>(samples.size());

        // 1. Оцінка постійного зміщення (DC Offset)
        const auto sum = std::accumulate(samples.begin(), samples.end(), std::complex<double>{0.0, 0.0});
        const auto dc = sum / count;

        // 2. Дисбаланс квадратурних гілок (IQ Imbalance)
        double p_i = 0.0;
        double p_q = 0.0;
        double cross_iq = 0.0;

        for (const auto& s : samples) {
            const double i_c = s.real() - dc.real();
            const double q_c = s.imag() - dc.imag();
            p_i += i_c * i_c;
            p_q += q_c * q_c;
            cross_iq += i_c * q_c;
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

        // 3. Зсув частоти несучої (CFO) через автокореляцію Муза
        std::complex<double> r_cross{0.0, 0.0};
        for (std::size_t k = 0; k < samples.size() - 1; ++k) {
            r_cross += samples[k + 1] * std::conj(samples[k]);
        }

        const double phase_diff = std::arg(r_cross);
        const double cfo_hz = (phase_diff * sample_rate_hz) / (2.0 * std::numbers::pi);

        const double signal_pwr = (p_i + p_q);
        const double snr_db = 10.0 * std::log10(signal_pwr + 1e-12);

        return Signature{
            .cfo_hz = cfo_hz,
            .iq_gain_imbalance = gain_imb,
            .iq_phase_skew_deg = phase_skew_deg,
            .dc_offset = dc,
            .snr_db = snr_db
        };
    }
};

class TdoaLocalizer {
public:
    [[nodiscard]] static std::expected<Point2D, AnalysisError>
    localize2D(std::span<const TdoaSensor> sensors, Point2D initial_guess) noexcept {
        if (sensors.size() < 3) {
            return std::unexpected(AnalysisError::InsufficientSamples);
        }

        double x = initial_guess.x;
        double y = initial_guess.y;
        constexpr int MaxIterations = 50;
        constexpr double Tolerance = 1e-5;

        for (int iter = 0; iter < MaxIterations; ++iter) {
            double d0 = std::hypot(x - sensors[0].pos.x, y - sensors[0].pos.y);
            if (d0 < 1e-4) d0 = 1e-4;

            double jtj00 = 0.0, jtj01 = 0.0, jtj11 = 0.0;
            double jtr0 = 0.0, jtr1 = 0.0;

            for (std::size_t i = 1; i < sensors.size(); ++i) {
                double di = std::hypot(x - sensors[i].pos.x, y - sensors[i].pos.y);
                if (di < 1e-4) di = 1e-4;

                const double measured_delta_d = SpeedOfLight * (sensors[i].timestamp_s - sensors[0].timestamp_s);
                const double calc_delta_d = di - d0;
                const double residual = measured_delta_d - calc_delta_d;

                const double j_x = ((x - sensors[i].pos.x) / di) - ((x - sensors[0].pos.x) / d0);
                const double j_y = ((y - sensors[i].pos.y) / di) - ((y - sensors[0].pos.y) / d0);

                jtj00 += j_x * j_x;
                jtj01 += j_x * j_y;
                jtj11 += j_y * j_y;

                jtr0 += j_x * residual;
                jtr1 += j_y * residual;
            }

            const double det = jtj00 * jtj11 - jtj01 * jtj01;
            if (std::abs(det) < 1e-12) {
                return std::unexpected(AnalysisError::CollinearSensors);
            }

            const double inv00 = jtj11 / det;
            const double inv01 = -jtj01 / det;
            const double inv11 = jtj00 / det;

            const double delta_x = inv00 * jtr0 + inv01 * jtr1;
            const double delta_y = inv01 * jtr0 + inv11 * jtr1;

            x += delta_x;
            y += delta_y;

            if (std::hypot(delta_x, delta_y) < Tolerance) {
                return Point2D{x, y};
            }
        }

        return Point2D{x, y};
    }
};

} // namespace rf

int main() {
    constexpr std::size_t N = 128;
    constexpr double Fs = 10'000'000.0;
    constexpr double TrueCfo = 45'200.0;
    std::vector<std::complex<double>> signal(N);

    for (std::size_t k = 0; k < N; ++k) {
        const double t = static_cast<double>(k) / Fs;
        const double phase = 2.0 * std::numbers::pi * TrueCfo * t;
        signal[k] = std::complex<double>(
            1.06 * std::cos(phase) + 0.03,
            0.94 * std::sin(phase + 4.0 * std::numbers::pi / 180.0) - 0.02
        );
    }

    if (const auto sig = rf::FingerprintAnalyzer::extract(signal, Fs)) {
        std::cout << "C++ RF Fingerprint:\n"
                  << "  CFO: " << sig->cfo_hz << " Hz\n"
                  << "  Gain Imbalance: " << sig->iq_gain_imbalance << "\n"
                  << "  Phase Skew: " << sig->iq_phase_skew_deg << " deg\n"
                  << "  DC Offset: " << sig->dc_offset << "\n";
    }

    const std::vector<rf::TdoaSensor> sensors = {
        { .pos = { .x = 0.0,    .y = 0.0 },    .timestamp_s = 0.000001000 },
        { .pos = { .x = 1000.0, .y = 0.0 },    .timestamp_s = 0.000002155 },
        { .pos = { .x = 500.0,  .y = 1000.0 }, .timestamp_s = 0.000001840 }
    };

    if (const auto target = rf::TdoaLocalizer::localize2D(sensors, {500.0, 500.0})) {
        std::cout << "C++ TDoA Target: X=" << target->x << " m, Y=" << target->y << " m\n";
    }

    return 0;
}
