#include <cstdint>
#include <cmath>
#include <vector>
#include <span>
#include <optional>
#include <string_view>

struct StepMetrics {
    double setpoint{0.0};
    double latency_ms{0.0};
    double rise_time_ms{0.0};
    double overshoot_pct{0.0};
    double settling_time_ms{0.0};
    double d_noise_rms{0.0};
    int    oscillation_count{0};
};

enum class TuneDiagnostic {
    Perfect,
    PLow,
    PHigh,
    DLow,
    DHighNoise,
    SystemLaggy
};

class StepResponseAnalyzer {
public:
    static std::optional<StepMetrics> analyze(std::span<const uint64_t> time_us,
                                              std::span<const double> target,
                                              std::span<const double> actual,
                                              std::span<const double> d_term) {
        const size_t n = time_us.size();
        if (n < 25 || target.size() != n || actual.size() != n || d_term.size() != n) {
            return std::nullopt;
        }

        const double t0 = target.front();
        const double t_final = target.back();
        const double step_amp = t_final - t0;

        if (std::abs(step_amp) < 35.0) {
            return std::nullopt; // Амплітуда сходинки недостатня для достовірної оцінки
        }

        // Перевірка спокою до початку сходинки
        for (size_t i = 0; i < 5 && i < n; ++i) {
            if (std::abs(target[i] - actual[i]) > 25.0) {
                return std::nullopt;
            }
        }

        StepMetrics m;
        m.setpoint = step_amp;

        const uint64_t t_start = time_us.front();
        uint64_t t_5pct = 0, t_10pct = 0, t_90pct = 0;
        double max_val = actual.front();
        size_t peak_idx = 0;

        const double target_5  = t0 + 0.05 * step_amp;
        const double target_10 = t0 + 0.10 * step_amp;
        const double target_90 = t0 + 0.90 * step_amp;
        const double band_low  = t_final - 0.05 * std::abs(step_amp);
        const double band_high = t_final + 0.05 * std::abs(step_amp);

        for (size_t i = 1; i < n; ++i) {
            const double val = actual[i];

            if (!t_5pct && ((step_amp > 0 && val >= target_5) || (step_amp < 0 && val <= target_5))) {
                t_5pct = time_us[i];
            }
            if (!t_10pct && ((step_amp > 0 && val >= target_10) || (step_amp < 0 && val <= target_10))) {
                t_10pct = time_us[i];
            }
            if (!t_90pct && ((step_amp > 0 && val >= target_90) || (step_amp < 0 && val <= target_90))) {
                t_90pct = time_us[i];
            }

            if (step_amp > 0) {
                if (val > max_val) { max_val = val; peak_idx = i; }
            } else {
                if (val < max_val) { max_val = val; peak_idx = i; }
            }
        }

        if (t_5pct > t_start) m.latency_ms = static_cast<double>(t_5pct - t_start) / 1000.0;
        if (t_90pct > t_10pct && t_10pct > 0) m.rise_time_ms = static_cast<double>(t_90pct - t_10pct) / 1000.0;

        if (step_amp > 0 && max_val > t_final) {
            m.overshoot_pct = ((max_val - t_final) / step_amp) * 100.0;
        } else if (step_amp < 0 && max_val < t_final) {
            m.overshoot_pct = ((t_final - max_val) / std::abs(step_amp)) * 100.0;
        }

        uint64_t t_settle = 0;
        int crossings = 0;
        for (size_t i = peak_idx; i < n; ++i) {
            if (actual[i] < band_low || actual[i] > band_high) {
                t_settle = time_us[i];
                crossings++;
            }
        }
        m.settling_time_ms = (t_settle > t_start) ? static_cast<double>(t_settle - t_start) / 1000.0 : m.rise_time_ms;
        m.oscillation_count = crossings;

        // Розрахунок високочастотного шуму D-терма на плато
        double sum_sq = 0.0;
        size_t noise_samples = 0;
        const size_t start_noise = n / 2;
        for (size_t i = start_noise + 1; i < n; ++i) {
            const double delta = d_term[i] - d_term[i - 1];
            sum_sq += delta * delta;
            noise_samples++;
        }
        m.d_noise_rms = (noise_samples > 0) ? std::sqrt(sum_sq / static_cast<double>(noise_samples)) : 0.0;

        return m;
    }

    static TuneDiagnostic evaluate(const StepMetrics &m) {
        if (m.latency_ms > 24.0) return TuneDiagnostic::SystemLaggy;
        if (m.d_noise_rms > 35.0) return TuneDiagnostic::DHighNoise;
        if (m.overshoot_pct > 20.0 && m.rise_time_ms < 32.0) {
            return (m.oscillation_count > 4) ? TuneDiagnostic::PHigh : TuneDiagnostic::DLow;
        }
        if (m.rise_time_ms > 90.0 && m.overshoot_pct < 2.0) {
            return TuneDiagnostic::PLow;
        }
        return TuneDiagnostic::Perfect;
    }

    static std::string_view recommendation(TuneDiagnostic diag) {
        switch (diag) {
            case TuneDiagnostic::Perfect:
                return "Контур ідеально збалансовано: мінімальний лаг, перерегулювання в межах 5-10%, чистий D-терм.";
            case TuneDiagnostic::PLow:
                return "Збільшити P на 15-20%: контур занадто повільно виходить на сходинку, бракує жорсткості.";
            case TuneDiagnostic::PHigh:
                return "Зменшити P на 15%: зафіксовано затяжні низькочастотні коливання (дзвін) навколо цільового значення.";
            case TuneDiagnostic::DLow:
                return "Збільшити D на 10-15%: наростання швидке, але спостерігається надмірний одиничний відскок (overshoot).";
            case TuneDiagnostic::DHighNoise:
                return "Зменшити D на 20% або активувати Dynamic Notch: критичний рівень ВЧ шуму, загроза перегріву моторів.";
            case TuneDiagnostic::SystemLaggy:
                return "Перевірити фільтри або демпфери IMU: затримка > 24 мс свідчить про надмірний фазовий лаг у системі.";
        }
        return "";
    }
};
