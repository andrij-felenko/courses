//
// phase_control_sim.cpp - Об'єктно-орієнтована модель фазового UJT-регулятора (C++20)
//
#include <iostream>
#include <iomanip>
#include <cmath>
#include <numbers>
#include <array>
#include <span>
#include <expected>
#include <string_view>

namespace electronics::power {

struct UjtParameters {
    double eta{0.65};          // Внутрішній коефіцієнт поділу (0.55...0.82)
    double v_diode{0.65};      // Прямий спад на p-n переході емітера, В
    double v_valley{1.50};     // Напруга западини, В
};

struct CircuitComponents {
    double v_grid_rms{230.0};  // Діюча напруга мережі, В
    double f_grid{50.0};       // Частота мережі, Гц
    double v_zener{20.0};      // Напруга синхронізації стабілітрона, В
    double r_min{5100.0};      // Постійний резистор, Ом
    double r_pot{100000.0};    // Змінний резистор (потенціометр), Ом
    double capacitance{100e-9};// Ємність часозадавального конденсатора, Ф
    double r_load{50.0};       // Активний опір навантаження (ТЕН, лампа), Ом
};

struct SimulationPoint {
    double pot_percentage{0.0};
    double r_total_kohm{0.0};
    double delay_ms{0.0};
    double firing_angle_deg{0.0};
    double v_rms_volts{0.0};
    double power_watts{0.0};
    double power_percentage{0.0};
    bool triggered{true};
};

enum class CalculationError {
    InvalidPotentiometerRange,
    ZenerVoltageTooLow,
};

class PhaseController {
public:
    constexpr explicit PhaseController(CircuitComponents components, UjtParameters ujt = {}) noexcept
        : comp_{components}, ujt_{ujt} {}

    [[nodiscard]] double peak_voltage() const noexcept {
        return ujt_.eta * comp_.v_zener + ujt_.v_diode;
    }

    [[nodiscard]] double half_period_ms() const noexcept {
        return 1000.0 / (2.0 * comp_.f_grid);
    }

    [[nodiscard]] std::expected<SimulationPoint, CalculationError>
    calculate_point(double pot_ratio) const noexcept {
        if (pot_ratio < 0.0 || pot_ratio > 1.0) {
            return std::unexpected(CalculationError::InvalidPotentiometerRange);
        }

        const double v_peak = peak_voltage();
        if (v_peak >= comp_.v_zener) {
            return std::unexpected(CalculationError::ZenerVoltageTooLow);
        }

        SimulationPoint pt;
        pt.pot_percentage = pot_ratio * 100.0;
        const double r_total = comp_.r_min + pot_ratio * comp_.r_pot;
        pt.r_total_kohm = r_total / 1000.0;

        const double num = comp_.v_zener - ujt_.v_valley;
        const double den = comp_.v_zener - v_peak;
        const double t_charge_sec = r_total * comp_.capacitance * std::log(num / den);
        const double t_charge_ms = t_charge_sec * 1000.0;
        const double t_half = half_period_ms();

        if (t_charge_ms >= t_half) {
            pt.triggered = false;
            pt.delay_ms = t_half;
            pt.firing_angle_deg = 180.0;
            pt.v_rms_volts = 0.0;
            pt.power_watts = 0.0;
            pt.power_percentage = 0.0;
        } else {
            pt.triggered = true;
            pt.delay_ms = t_charge_ms;
            pt.firing_angle_deg = (t_charge_ms / t_half) * 180.0;

            const double alpha_rad = pt.firing_angle_deg * (std::numbers::pi / 180.0);
            const double integral = (std::numbers::pi - alpha_rad) + (std::sin(2.0 * alpha_rad) / 2.0);
            pt.v_rms_volts = comp_.v_grid_rms * std::sqrt(integral / std::numbers::pi);
            pt.power_watts = (pt.v_rms_volts * pt.v_rms_volts) / comp_.r_load;

            const double p_max = (comp_.v_grid_rms * comp_.v_grid_rms) / comp_.r_load;
            pt.power_percentage = (pt.power_watts / p_max) * 100.0;
        }

        return pt;
    }

private:
    CircuitComponents comp_;
    UjtParameters ujt_;
};

} // namespace electronics::power

int main() {
    using namespace electronics::power;

    PhaseController controller{
        CircuitComponents{
            .v_grid_rms = 230.0,
            .f_grid = 50.0,
            .v_zener = 20.0,
            .r_min = 5100.0,
            .r_pot = 100000.0,
            .capacitance = 100e-9,
            .r_load = 50.0
        },
        UjtParameters{
            .eta = 0.65,
            .v_diode = 0.65,
            .v_valley = 1.50
        }
    };

    std::cout << "=== СИМУЛЯЦІЯ ФАЗОВОГО РЕГУЛЯТОРА НА UJT (C++20) ===\n";
    std::cout << std::fixed << std::setprecision(2);
    std::cout << "Поріг відмикання V_P = " << controller.peak_voltage() << " В\n";
    std::cout << "Тривалість напівперіоду = " << controller.half_period_ms() << " мс\n\n";

    std::cout << " Пот.%% |  Опір R, кОм | Час t, мс | Кут alpha | V_RMS, В | Потужність, Вт |  Потужн. %%\n";
    std::cout << "-------+--------------+-----------+-----------+----------+----------------+------------\n";

    constexpr std::array<double, 11> test_ratios{0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0};

    for (double ratio : test_ratios) {
        if (auto result = controller.calculate_point(ratio); result.has_value()) {
            const auto& pt = *result;
            std::cout << " " << std::setw(4) << std::setprecision(0) << pt.pot_percentage << "% | "
                      << std::setw(12) << std::setprecision(2) << pt.r_total_kohm << " | "
                      << std::setw(9) << std::setprecision(3) << pt.delay_ms << " | "
                      << std::setw(8) << std::setprecision(1) << pt.firing_angle_deg << "* | "
                      << std::setw(8) << std::setprecision(2) << pt.v_rms_volts << " | "
                      << std::setw(14) << std::setprecision(2) << pt.power_watts << " | "
                      << std::setw(10) << std::setprecision(1) << pt.power_percentage << "%\n";
        }
    }

    return 0;
}
