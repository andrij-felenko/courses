#include <iostream>
#include <vector>
#include <span>
#include <cmath>
#include <optional>
#include <algorithm>

namespace emeter {

struct PowerMetrics {
    double active_power{0.0};      // P, Активна потужність (Вт)
    double reactive_power{0.0};    // Q, Реактивна потужність (вар)
    double apparent_power{0.0};    // S, Повна потужність (В·А)
    double v_rms{0.0};             // Vrms, Діюча напруга (В)
    double i_rms{0.0};             // Irms, Діючий струм (А)
    double power_factor{1.0};      // PF, Коефіцієнт потужності
    double p_max{0.0};             // Пікова миттєва потужність (Вт)
    double p_min{0.0};             // Мінімальна миттєва потужність (Вт)
};

class PowerMeter {
public:
    // Обчислення метрологічних показників з використанням C++20 std::span
    [[nodiscard]] static std::optional<PowerMetrics> calculate(
        std::span<const double> voltages,
        std::span<const double> currents) noexcept 
    {
        if (voltages.empty() || voltages.size() != currents.size()) {
            return std::nullopt;
        }

        const size_t count = voltages.size();
        double sum_p = 0.0;
        double sum_v2 = 0.0;
        double sum_i2 = 0.0;
        double p_max = -1e9;
        double p_min = 1e9;

        for (size_t n = 0; n < count; ++n) {
            const double v = voltages[n];
            const double i = currents[n];
            const double p_inst = v * i;

            sum_p += p_inst;
            sum_v2 += v * v;
            sum_i2 += i * i;

            p_max = std::max(p_max, p_inst);
            p_min = std::min(p_min, p_inst);
        }

        const double inv_count = 1.0 / static_cast<double>(count);
        PowerMetrics m;
        m.active_power = sum_p * inv_count;
        m.v_rms = std::sqrt(sum_v2 * inv_count);
        m.i_rms = std::sqrt(sum_i2 * inv_count);
        m.apparent_power = m.v_rms * m.i_rms;

        const double diff = (m.apparent_power * m.apparent_power) - (m.active_power * m.active_power);
        m.reactive_power = (diff > 0.0) ? std::sqrt(diff) : 0.0;

        if (m.apparent_power > 1e-6) {
            m.power_factor = std::clamp(m.active_power / m.apparent_power, -1.0, 1.0);
        } else {
            m.power_factor = 1.0;
        }

        m.p_max = p_max;
        m.p_min = p_min;

        return m;
    }
};

} // namespace emeter
