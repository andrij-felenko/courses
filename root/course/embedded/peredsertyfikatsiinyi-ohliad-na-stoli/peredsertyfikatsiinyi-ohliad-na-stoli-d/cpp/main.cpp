#include <iostream>
#include <vector>
#include <span>
#include <string_view>
#include <optional>
#include <cmath>
#include <algorithm>
#include <numeric>
#include <format>

struct SpectrumBin {
    double freq_hz{0.0};
    double power_dbm{0.0};
};

struct KnownSource {
    std::string_view name;
    double fund_freq_hz{0.0};
    double tolerance_hz{50000.0};
};

struct DetectedPeak {
    double freq_hz{0.0};
    double power_dbm{0.0};
    double delta_over_floor_db{0.0};
    std::string_view matched_source{"Невідоме джерело"};
    int harmonic_order{0};
};

class EmcPeakAnalyzer {
public:
    explicit EmcPeakAnalyzer(int window_half_width = 8, double threshold_delta_db = 10.0)
        : window_half_width_{window_half_width}, threshold_delta_db_{threshold_delta_db} {}

    [[nodiscard]] std::vector<DetectedPeak> analyze(
        std::span<const SpectrumBin> spectrum,
        std::span<const KnownSource> sources) const {
        
        std::vector<DetectedPeak> detected_peaks;
        const int n = static_cast<int>(spectrum.size());
        if (n < 2 * window_half_width_ + 1) return detected_peaks;

        for (int i = window_half_width_; i < n - window_half_width_; ++i) {
            // Перевірка на локальний максимум
            if (spectrum[i].power_dbm <= spectrum[i - 1].power_dbm ||
                spectrum[i].power_dbm <= spectrum[i + 1].power_dbm) {
                continue;
            }

            // Розрахунок середньої підлоги шуму у ковзному вікні (без верхівки)
            double sum_noise = 0.0;
            int count = 0;
            for (int w = -window_half_width_; w <= window_half_width_; ++w) {
                if (std::abs(w) <= 1) continue;
                sum_noise += spectrum[i + w].power_dbm;
                count++;
            }
            const double local_floor = (count > 0) ? (sum_noise / count) : spectrum[i].power_dbm;
            const double delta = spectrum[i].power_dbm - local_floor;

            if (delta >= threshold_delta_db_) {
                DetectedPeak peak{
                    .freq_hz = spectrum[i].freq_hz,
                    .power_dbm = spectrum[i].power_dbm,
                    .delta_over_floor_db = delta
                };

                // Зіставлення з відомими тактовими генераторами
                for (const auto& src : sources) {
                    const double ratio = peak.freq_hz / src.fund_freq_hz;
                    const int order = static_cast<int>(std::round(ratio));
                    if (order >= 1) {
                        const double expected_freq = order * src.fund_freq_hz;
                        if (std::abs(peak.freq_hz - expected_freq) <= src.tolerance_hz) {
                            peak.matched_source = src.name;
                            peak.harmonic_order = order;
                            break;
                        }
                    }
                }
                detected_peaks.push_back(peak);
            }
        }
        return detected_peaks;
    }

private:
    int window_half_width_{8};
    double threshold_delta_db_{10.0};
};
