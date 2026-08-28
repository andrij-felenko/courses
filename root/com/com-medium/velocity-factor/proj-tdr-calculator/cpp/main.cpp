#include <iostream>
#include <cmath>
#include <optional>
#include <format>

namespace rf_physics {

constexpr double C_VACUUM_MM_PS = 0.299792458; // Швидкість світла у мм/пс

struct TdrParams {
    double velocity_factor; // Коефіцієнт укорочення
    double delta_t_ps;      // Затримка відбитого імпульсу (пс)
};

struct TdrMeasurement {
    double distance_mm;       // Відстань до пошкодження
    double propagation_delay; // Погонна затримка (пс/мм)
};

struct TraceSkew {
    double time_skew_ps;    // Часовий розсинхронізм
    double meander_len_mm;  // Необхідна довжина меандру
};

class SignalVelocityCalculator {
public:
    // Обчислення параметрів TDR із використанням std::optional для обробки помилок
    [[nodiscard]] static std::optional<TdrMeasurement> compute_tdr(const TdrParams& params) noexcept {
        if (params.velocity_factor <= 0.0 || params.velocity_factor > 1.0 || params.delta_t_ps < 0.0) {
            return std::nullopt;
        }

        const double v_signal = C_VACUUM_MM_PS * params.velocity_factor;
        const double distance = (v_signal * params.delta_t_ps) / 2.0;
        const double t_pd = 1.0 / v_signal;

        return TdrMeasurement{ .distance_mm = distance, .propagation_delay = t_pd };
    }

    // Обчислення міжканального розсинхронізму трас
    [[nodiscard]] static std::optional<TraceSkew> compute_skew(double len1_mm, double len2_mm, double vf) noexcept {
        if (vf <= 0.0 || vf > 1.0 || len1_mm < 0.0 || len2_mm < 0.0) {
            return std::nullopt;
        }

        const double v_signal = C_VACUUM_MM_PS * vf;
        const double t_pd = 1.0 / v_signal;
        const double skew = std::abs(len1_mm - len2_mm) * t_pd;
        const double diff_len = std::abs(len1_mm - len2_mm);

        return TraceSkew{ .time_skew_ps = skew, .meander_len_mm = diff_len };
    }
};

} // namespace rf_physics

int main() {
    using namespace rf_physics;

    // Приклад TDR-вимірювання коаксіального кабелю RG-58 (VF = 0.66)
    constexpr TdrParams cable_params{ .velocity_factor = 0.66, .delta_t_ps = 101010.0 };
    if (const auto res = SignalVelocityCalculator::compute_tdr(cable_params)) {
        std::cout << "--- TDR Рефлектометрія (C++) ---\n";
        std::cout << "Відстань до обриву: " << res->distance_mm / 1000.0 << " м\n";
        std::cout << "Погонна затримка:   " << res->propagation_delay << " пс/мм\n";
    }

    // Приклад вирівнювання трас на платі FR-4 (VF = 0.55)
    if (const auto skew = SignalVelocityCalculator::compute_skew(120.0, 135.0, 0.55)) {
        std::cout << "\n--- Вирівнювання трас (C++) ---\n";
        std::cout << "Часовий зсув:       " << skew->time_skew_ps << " пс\n";
        std::cout << "Довжина меандру:    " << skew->meander_len_mm << " мм\n";
    }

    return 0;
}
