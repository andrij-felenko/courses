#include <iostream>
#include <iomanip>
#include <numbers>
#include <cmath>
#include <expected>
#include <string_view>

struct RingingMeasureInput {
    double f1_hz{0.0};
    double f2_hz{0.0};
    double c_test_f{0.0};
    double v_in_volts{0.0};
    double f_sw_hz{0.0};
};

struct SnubberResult {
    double c_par_f{0.0};
    double l_par_h{0.0};
    double z0_ohms{0.0};
    double r_snub_ohms{0.0};
    double c_snub_f{0.0};
    double p_loss_watts{0.0};
};

enum class SnubberCalcError {
    InvalidFrequency,
    FrequencyNotShifted,
    InvalidCapacitance,
    ZeroVoltageOrSwitching
};

constexpr std::expected<SnubberResult, SnubberCalcError> calculate_snubber(const RingingMeasureInput& in) noexcept {
    if (in.f1_hz <= 0.0 || in.f2_hz <= 0.0) {
        return std::unexpected(SnubberCalcError::InvalidFrequency);
    }
    if (in.f2_hz >= in.f1_hz) {
        return std::unexpected(SnubberCalcError::FrequencyNotShifted);
    }
    if (in.c_test_f <= 0.0) {
        return std::unexpected(SnubberCalcError::InvalidCapacitance);
    }
    if (in.v_in_volts <= 0.0 || in.f_sw_hz <= 0.0) {
        return std::unexpected(SnubberCalcError::ZeroVoltageOrSwitching);
    }

    const double ratio = in.f1_hz / in.f2_hz;
    const double c_par = in.c_test_f / (ratio * ratio - 1.0);
    const double omega1 = 2.0 * std::numbers::pi * in.f1_hz;
    const double l_par = 1.0 / (omega1 * omega1 * c_par);
    const double z0 = std::sqrt(l_par / c_par);
    const double c_snub = 3.0 * c_par;
    const double p_loss = c_snub * (in.v_in_volts * in.v_in_volts) * in.f_sw_hz;

    return SnubberResult{
        .c_par_f = c_par,
        .l_par_h = l_par,
        .z0_ohms = z0,
        .r_snub_ohms = z0,
        .c_snub_f = c_snub,
        .p_loss_watts = p_loss
    };
}

int main() {
    constexpr RingingMeasureInput meas{
        .f1_hz = 180.0e6,
        .f2_hz = 115.0e6,
        .c_test_f = 470.0e-12,
        .v_in_volts = 24.0,
        .f_sw_hz = 500.0e3
    };

    const auto res = calculate_snubber(meas);
    if (res) {
        std::cout << std::fixed << std::setprecision(2);
        std::cout << "--- Параметри паразитного контуру ---\n";
        std::cout << "Паразитна ємність C_par:     " << res->c_par_f * 1e12 << " пФ\n";
        std::cout << "Паразитна індуктивність L_par: " << res->l_par_h * 1e9 << " нГн\n";
        std::cout << "Характеристичний опір Z0:    " << res->z0_ohms << " Ом\n\n";
        std::cout << "--- Розраховані номінали снубера ---\n";
        std::cout << "Резистор R_snub:              " << res->r_snub_ohms << " Ом\n";
        std::cout << "Конденсатор C_snub:           " << res->c_snub_f * 1e12 << " пФ\n";
        std::cout << "Теплові втрати на резисторі:  " << std::setprecision(3) << res->p_loss_watts << " Вт\n";
    } else {
        std::cerr << "Помилка розрахунку параметрів снубера!\n";
    }
    return 0;
}
