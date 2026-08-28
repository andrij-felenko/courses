// FastenerCalculator.hpp - Ідіоматичний C++20 калькулятор різьбових з'єднань
#include <iostream>
#include <cmath>
#include <numbers>
#include <string_view>
#include <array>

namespace drone::mechanics {

enum class BoltGrade {
    Grade8_8,
    Grade10_9,
    Grade12_9,
    StainlessA2_70
};

enum class LubricationState {
    DrySteel,
    Threadlocker,
    Oiled
};

struct FastenerSpec {
    double nominal_dia_mm{3.0};
    double pitch_mm{0.5};
    double bearing_inner_dia_mm{3.4};
    double bearing_outer_dia_mm{7.0};
    BoltGrade grade{BoltGrade::Grade10_9};
    LubricationState lube{LubricationState::Threadlocker};
    double clamp_material_limit_mpa{140.0};
    double thread_shear_limit_mpa{150.0};
};

struct FastenerResult {
    double stress_area_mm2{0.0};
    double target_preload_n{0.0};
    double tightening_torque_nm{0.0};
    double bearing_pressure_mpa{0.0};
    bool is_bearing_safe{false};
    double min_thread_engagement_mm{0.0};

    [[nodiscard]] constexpr double engagement_ratio(double nom_dia) const noexcept {
        return min_thread_engagement_mm / nom_dia;
    }
};

class JointCalculator {
public:
    [[nodiscard]] static constexpr double yield_strength(BoltGrade g) noexcept {
        switch (g) {
            case BoltGrade::Grade8_8:        return 640.0;
            case BoltGrade::Grade10_9:       return 940.0;
            case BoltGrade::Grade12_9:       return 1080.0;
            case BoltGrade::StainlessA2_70:  return 450.0;
        }
        return 640.0;
    }

    [[nodiscard]] static constexpr double tensile_strength(BoltGrade g) noexcept {
        switch (g) {
            case BoltGrade::Grade8_8:        return 800.0;
            case BoltGrade::Grade10_9:       return 1040.0;
            case BoltGrade::Grade12_9:       return 1220.0;
            case BoltGrade::StainlessA2_70:  return 700.0;
        }
        return 800.0;
    }

    [[nodiscard]] static constexpr std::pair<double, double> friction_coefficients(LubricationState l) noexcept {
        switch (l) {
            case LubricationState::DrySteel:      return {0.20, 0.20};
            case LubricationState::Threadlocker:  return {0.13, 0.13};
            case LubricationState::Oiled:         return {0.10, 0.10};
        }
        return {0.20, 0.20};
    }

    [[nodiscard]] static FastenerResult evaluate(const FastenerSpec& spec) noexcept {
        FastenerResult res;
        const double d = spec.nominal_dia_mm;
        const double p = spec.pitch_mm;

        // 1. Площа перерізу стрижня ISO 898-1
        const double d_s = d - 0.9382 * p;
        res.stress_area_mm2 = (std::numbers::pi / 4.0) * d_s * d_s;

        // 2. Цільовий натяг болта: 85% від границі текучості
        const double r_p02 = yield_strength(spec.grade);
        res.target_preload_n = 0.85 * res.stress_area_mm2 * r_p02;

        // 3. Момент затягування за VDI 2230
        const auto [mu_th, mu_b] = friction_coefficients(spec.lube);
        const double d_2 = d - 0.64952 * p;
        const double r_b = (spec.bearing_outer_dia_mm + spec.bearing_inner_dia_mm) / 4.0;
        constexpr double cos_half_alpha = 0.8660254037844386; // cos(30°)

        const double term_pitch   = p / (2.0 * std::numbers::pi);
        const double term_thread  = (mu_th * d_2) / (2.0 * cos_half_alpha);
        const double term_bearing = mu_b * r_b;

        res.tightening_torque_nm = res.target_preload_n * (term_pitch + term_thread + term_bearing) / 1000.0;

        // 4. Тиск на опорну площину
        const double dw = spec.bearing_outer_dia_mm;
        const double dh = spec.bearing_inner_dia_mm;
        const double a_bearing = (std::numbers::pi / 4.0) * (dw * dw - dh * dh);

        res.bearing_pressure_mpa = res.target_preload_n / a_bearing;
        res.is_bearing_safe = (res.bearing_pressure_mpa <= spec.clamp_material_limit_mpa);

        // 5. Глибина зачеплення в алюмінії проти зрізу витків
        const double r_m = tensile_strength(spec.grade);
        const double shear_area_factor = std::numbers::pi * d * 0.75;
        res.min_thread_engagement_mm = 1.25 * (res.stress_area_mm2 * r_m) / 
                                       (shear_area_factor * spec.thread_shear_limit_mpa);

        return res;
    }
};

} // namespace drone::mechanics

int main() {
    using namespace drone::mechanics;

    constexpr FastenerSpec spec_m3{
        .nominal_dia_mm = 3.0,
        .pitch_mm = 0.5,
        .bearing_inner_dia_mm = 3.4,
        .bearing_outer_dia_mm = 7.0,
        .grade = BoltGrade::Grade10_9,
        .lube = LubricationState::Threadlocker,
        .clamp_material_limit_mpa = 140.0,
        .thread_shear_limit_mpa = 150.0
    };

    const auto r = JointCalculator::evaluate(spec_m3);

    std::cout << "=== Розрахунок кріплення M3 (клас 10.9) у карбон та алюміній [C++20] ===\n";
    std::cout << "Площа розтягу A_s:          " << r.stress_area_mm2 << " мм²\n";
    std::cout << "Рекомендований натяг F_p:   " << r.target_preload_n << " Н\n";
    std::cout << "Момент затягування T:       " << r.tightening_torque_nm << " Н·м\n";
    std::cout << "Контактний тиск під шайбою: " << r.bearing_pressure_mpa << " МПа ["
              << (r.is_bearing_safe ? "БЕЗПЕЧНО" : "УВАГА: РОЗДАВЛЮВАННЯ") << "]\n";
    std::cout << "Мін. довжина різьби в 6061: " << r.min_thread_engagement_mm << " мм ("
              << r.engagement_ratio(spec_m3.nominal_dia_mm) << " · d)\n";

    return 0;
}
