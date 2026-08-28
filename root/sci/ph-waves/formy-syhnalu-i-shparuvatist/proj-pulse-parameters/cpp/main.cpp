#include <cmath>
#include <cstdint>
#include <chrono>
#include <span>
#include <optional>
#include <expected>
#include <concepts>
#include <algorithm>

namespace signal_dsp {

/* Метрики імпульсного сигналу */
struct PulseMetrics {
    double frequency_hz{0.0};
    std::chrono::duration<double> period{0.0};
    std::chrono::duration<double> pulse_width{0.0};
    double duty_cycle{0.0};   // D = th / T
    double duty_factor{0.0};  // S = 1 / D
    double crest_factor{0.0}; // Kc = Vpeak / Vrms
};

/* Коди помилок аналізу */
enum class PulseError {
    ZeroPeriod,
    PulseWidthExceedsPeriod,
    InvalidClockRate,
    NoData
};

/* Концепт для беззнакових цілих типів лічильника таймера */
template <typename T>
concept UnsignedIntegral = std::unsigned_integral<T>;

/* Шаблонний клас обробки подій захоплення таймера */
template <UnsignedIntegral TickType = uint32_t>
class PulseCaptureAnalyzer {
public:
    constexpr explicit PulseCaptureAnalyzer(uint32_t timer_clock_hz) noexcept
        : clock_hz_(timer_clock_hz) {}

    void on_falling_edge(TickType tick) noexcept {
        if (has_rising_) {
            last_fall_ = tick;
            has_falling_ = true;
        }
    }

    [[nodiscard]] std::expected<PulseMetrics, PulseError> on_rising_edge(TickType tick) noexcept {
        if (clock_hz_ == 0) {
            return std::unexpected(PulseError::InvalidClockRate);
        }

        std::optional<PulseMetrics> result;

        if (has_rising_ && has_falling_) {
            // Беззнакове віднімання автоматично враховує переповнення лічильника
            const TickType period_ticks = tick - last_rise_;
            const TickType high_ticks = last_fall_ - last_rise_;

            if (period_ticks == 0) {
                return std::unexpected(PulseError::ZeroPeriod);
            }
            if (high_ticks > period_ticks) {
                return std::unexpected(PulseError::PulseWidthExceedsPeriod);
            }

            const double clk = static_cast<double>(clock_hz_);
            const double period_s = static_cast<double>(period_ticks) / clk;
            const double width_s  = static_cast<double>(high_ticks) / clk;
            const double duty     = static_cast<double>(high_ticks) / static_cast<double>(period_ticks);

            PulseMetrics m{
                .frequency_hz = clk / static_cast<double>(period_ticks),
                .period = std::chrono::duration<double>(period_s),
                .pulse_width = std::chrono::duration<double>(width_s),
                .duty_cycle = duty,
                .duty_factor = (high_ticks > 0) ? (1.0 / duty) : 0.0,
                .crest_factor = (duty > 0.0) ? (1.0 / std::sqrt(duty)) : 0.0
            };
            result = m;
        }

        last_rise_ = tick;
        has_rising_ = true;
        has_falling_ = false;

        if (result) {
            return *result;
        }
        return std::unexpected(PulseError::NoData);
    }

    void reset() noexcept {
        has_rising_ = false;
        has_falling_ = false;
    }

private:
    uint32_t clock_hz_{0};
    TickType last_rise_{0};
    TickType last_fall_{0};
    bool has_rising_{false};
    bool has_falling_{false};
};

/* Структура результату аналізу дискретних вибірок */
struct WaveformStatistics {
    float mean_dc{0.0f};
    float rms{0.0f};
    float crest_factor{0.0f};
    float form_factor{0.0f};
};

/* Розрахунок інтегральних норм через std::span без зайвого копіювання пам'яті */
[[nodiscard]] inline std::expected<WaveformStatistics, PulseError>
calculate_statistics(std::span<const float> samples) noexcept {
    if (samples.empty()) {
        return std::unexpected(PulseError::NoData);
    }

    double sum = 0.0;
    double sum_sq = 0.0;
    double sum_abs = 0.0;
    float peak = 0.0f;

    for (const float val : samples) {
        const double dval = static_cast<double>(val);
        sum += dval;
        sum_sq += dval * dval;
        const float abs_val = std::abs(val);
        sum_abs += static_cast<double>(abs_val);
        peak = std::max(peak, abs_val);
    }

    const double n = static_cast<double>(samples.size());
    const double mean = sum / n;
    const double rms = std::sqrt(sum_sq / n);
    const double rectified_avg = sum_abs / n;

    WaveformStatistics stats{
        .mean_dc = static_cast<float>(mean),
        .rms = static_cast<float>(rms),
        .crest_factor = (rms > 1e-9) ? static_cast<float>(peak / rms) : 0.0f,
        .form_factor = (rectified_avg > 1e-9) ? static_cast<float>(rms / rectified_avg) : 0.0f
    };

    return stats;
}

} // namespace signal_dsp
