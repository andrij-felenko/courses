#include <iostream>
#include <cmath>
#include <numbers>
#include <string_view>
#include <expected>
#include <iomanip>
#include <algorithm>

enum class PolarizationState {
    Linear,
    CircularRHCP,
    CircularLHCP,
    EllipticalRHCP,
    EllipticalLHCP
};

struct FieldInput {
    double ex0{1.0};
    double ey0{1.0};
    double delta_deg{90.0};
};

struct PolarizationAnalysis {
    double s0{0.0}, s1{0.0}, s2{0.0}, s3{0.0};
    double s1_norm{0.0}, s2_norm{0.0}, s3_norm{0.0};
    double major_axis{0.0};
    double minor_axis{0.0};
    double tilt_deg{0.0};
    double ellipticity_deg{0.0};
    double ar_linear{1.0};
    double ar_db{0.0};
    PolarizationState state{PolarizationState::CircularRHCP};
    double plf_linear_h{0.5};
    double plf_rhcp{1.0};
};

enum class AnalysisError {
    ZeroFieldMagnitude,
    InvalidPhase
};

constexpr double deg_to_rad(double deg) noexcept {
    return deg * std::numbers::pi / 180.0;
}

constexpr double rad_to_deg(double rad) noexcept {
    return rad * 180.0 / std::numbers::pi;
}

std::expected<PolarizationAnalysis, AnalysisError> 
analyze_polarization(const FieldInput& input) noexcept {
    if (input.ex0 <= 0.0 && input.ey0 <= 0.0) {
        return std::unexpected(AnalysisError::ZeroFieldMagnitude);
    }

    PolarizationAnalysis res;
    const double delta = deg_to_rad(input.delta_deg);
    const double ex2 = input.ex0 * input.ex0;
    const double ey2 = input.ey0 * input.ey0;

    res.s0 = ex2 + ey2;
    res.s1 = ex2 - ey2;
    res.s2 = 2.0 * input.ex0 * input.ey0 * std::cos(delta);
    res.s3 = 2.0 * input.ex0 * input.ey0 * std::sin(delta);

    if (res.s0 > 1e-12) {
        res.s1_norm = res.s1 / res.s0;
        res.s2_norm = res.s2 / res.s0;
        res.s3_norm = res.s3 / res.s0;
    }

    const double two_tau = std::atan2(res.s2, res.s1);
    res.tilt_deg = rad_to_deg(two_tau / 2.0);

    const double sin_two_chi = std::clamp(res.s3_norm, -1.0, 1.0);
    const double two_chi = std::asin(sin_two_chi);
    res.ellipticity_deg = rad_to_deg(two_chi / 2.0);

    const double e_total = std::sqrt(res.s0);
    res.major_axis = e_total * std::cos(two_chi / 2.0);
    res.minor_axis = e_total * std::abs(std::sin(two_chi / 2.0));

    const double abs_tan_chi = std::abs(std::tan(two_chi / 2.0));
    if (abs_tan_chi < 1e-6) {
        res.ar_linear = 1e6;
        res.ar_db = 99.9;
    } else {
        res.ar_linear = 1.0 / abs_tan_chi;
        res.ar_db = 20.0 * std::log10(res.ar_linear);
    }

    if (res.ar_db > 20.0) {
        res.state = PolarizationState::Linear;
    } else if (res.ar_db < 0.5) {
        res.state = (res.s3 > 0) ? PolarizationState::CircularRHCP : PolarizationState::CircularLHCP;
    } else {
        res.state = (res.s3 > 0) ? PolarizationState::EllipticalRHCP : PolarizationState::EllipticalLHCP;
    }

    res.plf_linear_h = 0.5 * (1.0 + res.s1_norm);
    res.plf_rhcp = 0.5 * (1.0 + res.s3_norm);

    return res;
}

constexpr std::string_view state_to_string(PolarizationState s) noexcept {
    switch (s) {
        case PolarizationState::Linear:         return "Лінійна (Linear)";
        case PolarizationState::CircularRHCP:   return "Чиста колова RHCP";
        case PolarizationState::CircularLHCP:   return "Чиста колова LHCP";
        case PolarizationState::EllipticalRHCP: return "Еліптична (Праве обертання / RHCP)";
        case PolarizationState::EllipticalLHCP: return "Еліптична (Ліве обертання / LHCP)";
    }
    return "Невідома";
}

int main() {
    constexpr FieldInput input{ .ex0 = 1.0, .ey0 = 0.8, .delta_deg = 80.0 };

    if (auto result = analyze_polarization(input); result.has_value()) {
        const auto& res = result.value();
        std::cout << std::fixed << std::setprecision(3);
        std::cout << "=== Результати аналізу поляризаційного еліпса (C++20) ===\n";
        std::cout << "Нормований вектор Стокса: s1=" << res.s1_norm 
                  << ", s2=" << res.s2_norm << ", s3=" << res.s3_norm << "\n";
        std::cout << "Кут нахилу (tau): " << res.tilt_deg << " deg\n";
        std::cout << "Кут еліптичності (chi): " << res.ellipticity_deg << " deg\n";
        std::cout << "Осьове відношення (AR): " << res.ar_linear << " (" << res.ar_db << " дБ)\n";
        std::cout << "Класифікація стану: " << state_to_string(res.state) << "\n";
        std::cout << "PLF при прийомі H-антеною: " << res.plf_linear_h 
                  << " (" << 10.0 * std::log10(res.plf_linear_h) << " дБ)\n";
        std::cout << "PLF при прийомі RHCP-антеною: " << res.plf_rhcp 
                  << " (" << 10.0 * std::log10(res.plf_rhcp) << " дБ)\n";
    } else {
        std::cerr << "Помилка аналізу: нульова амплітуда поля!\n";
    }

    return 0;
}
