// q_measurement.hpp — Ідіоматична C++20 реалізація
#pragma once

#include <vector>
#include <span>
#include <optional>
#include <cmath>
#include <numeric>
#include <numbers>
#include <algorithm>

namespace physics::oscillations {

struct RingdownResult {
    double q_factor{0.0};
    double r_squared{0.0};
    double initial_amplitude{0.0};
};

struct BandwidthResult {
    double q_factor{0.0};
    double f0_hz{0.0};
    double bandwidth_hz{0.0};
};

class QMeter {
public:
    static std::optional<RingdownResult> measureRingdown(
        std::span<const double> samples,
        double sample_rate_hz,
        double f0_hz,
        double noise_floor = 1e-4
    ) {
        if (samples.size() < 10 || sample_rate_hz <= 0.0 || f0_hz <= 0.0) {
            return std::nullopt;
        }

        struct Peak { double time; double log_amp; };
        std::vector<Peak> peaks;
        peaks.reserve(samples.size() / 10);

        for (size_t i = 1; i < samples.size() - 1; ++i) {
            if (samples[i] > samples[i - 1] && samples[i] > samples[i + 1] && samples[i] > noise_floor) {
                double t = static_cast<double>(i) / sample_rate_hz;
                peaks.push_back({t, std::log(samples[i])});
            }
        }

        if (peaks.size() < 3) {
            return std::nullopt;
        }

        double n = static_cast<double>(peaks.size());
        double sum_t = 0.0, sum_y = 0.0, sum_tt = 0.0, sum_ty = 0.0;

        for (const auto& p : peaks) {
            sum_t += p.time;
            sum_y += p.log_amp;
            sum_tt += p.time * p.time;
            sum_ty += p.log_amp * p.time;
        }

        double denom = n * sum_tt - sum_t * sum_t;
        if (std::abs(denom) < 1e-12) {
            return std::nullopt;
        }

        double slope = (n * sum_ty - sum_t * sum_y) / denom;
        double intercept = (sum_y - slope * sum_t) / n;

        if (slope >= 0.0) {
            return std::nullopt;
        }

        double mean_y = sum_y / n;
        double ss_tot = 0.0, ss_res = 0.0;
        for (const auto& p : peaks) {
            double y_pred = intercept + slope * p.time;
            ss_tot += (p.log_amp - mean_y) * (p.log_amp - mean_y);
            ss_res += (p.log_amp - y_pred) * (p.log_amp - y_pred);
        }

        double r_sq = (ss_tot > 0.0) ? (1.0 - (ss_res / ss_tot)) : 0.0;
        if (r_sq < 0.80) {
            return std::nullopt;
        }

        return RingdownResult{
            .q_factor = -(std::numbers::pi * f0_hz) / slope,
            .r_squared = r_sq,
            .initial_amplitude = std::exp(intercept)
        };
    }

    static std::optional<BandwidthResult> measure3dB(
        std::span<const double> spectrum_amp,
        std::span<const double> freqs_hz
    ) {
        if (spectrum_amp.size() != freqs_hz.size() || spectrum_amp.size() < 5) {
            return std::nullopt;
        }

        auto max_it = std::max_element(spectrum_amp.begin(), spectrum_amp.end());
        size_t max_idx = std::distance(spectrum_amp.begin(), max_it);
        double max_amp = *max_it;

        if (max_amp <= 0.0 || max_idx == 0 || max_idx == spectrum_amp.size() - 1) {
            return std::nullopt;
        }

        double target_amp = max_amp / std::numbers::sqrt2;

        double f1 = freqs_hz.front();
        for (size_t i = max_idx; i > 0; --i) {
            if (spectrum_amp[i - 1] <= target_amp) {
                double a1 = spectrum_amp[i - 1], a2 = spectrum_amp[i];
                f1 = freqs_hz[i - 1] + (target_amp - a1) * (freqs_hz[i] - freqs_hz[i - 1]) / (a2 - a1);
                break;
            }
        }

        double f2 = freqs_hz.back();
        for (size_t i = max_idx; i < spectrum_amp.size() - 1; ++i) {
            if (spectrum_amp[i + 1] <= target_amp) {
                double a1 = spectrum_amp[i], a2 = spectrum_amp[i + 1];
                f2 = freqs_hz[i] + (target_amp - a1) * (freqs_hz[i + 1] - freqs_hz[i]) / (a2 - a1);
                break;
            }
        }

        double bw = f2 - f1;
        if (bw <= 0.0) {
            return std::nullopt;
        }

        return BandwidthResult{
            .q_factor = freqs_hz[max_idx] / bw,
            .f0_hz = freqs_hz[max_idx],
            .bandwidth_hz = bw
        };
    }
};

} // namespace physics::oscillations
