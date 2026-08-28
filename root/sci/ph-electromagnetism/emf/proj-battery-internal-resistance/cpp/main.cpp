#include <iostream>
#include <vector>
#include <optional>
#include <algorithm>

namespace power_system {

struct BatteryParameters {
    double nominal_emf{3.7};      // Початкова ЕРС (В)
    double internal_r_init{0.15}; // Початковий внутрішній опір (Ом)
    double capacity_ah{2.0};      // Ємність (А·год)
    double current_soc{100.0};    // Заряд (%)
};

struct StepResult {
    double terminal_voltage{0.0}; // Напруга на клемах (В)
    double current{0.0};          // Струм (А)
    double power_load{0.0};       // Потужність навантаження (Вт)
    double power_loss{0.0};       // Теплові втрати в джерелі (Вт)
    bool reset_warning{false};    // Попередження про просідання
};

class BatterySimulator {
public:
    explicit BatterySimulator(BatteryParameters params) 
        : params_(params) {}

    [[nodiscard]] double emf() const noexcept {
        const double soc_norm = params_.current_soc / 100.0;
        return 3.0 + 1.2 * soc_norm;
    }

    [[nodiscard]] double internal_resistance() const noexcept {
        const double soc_norm = params_.current_soc / 100.0;
        if (soc_norm < 0.20) {
            const double factor = (0.20 - soc_norm) / 0.20;
            return params_.internal_r_init * (1.0 + 3.0 * factor * factor);
        }
        return params_.internal_r_init;
    }

    StepResult simulate_step(double r_load_ohms, double dt_seconds) {
        StepResult result;
        const double cur_emf = emf();
        const double cur_r = internal_resistance();

        result.current = cur_emf / (r_load_ohms + cur_r);
        result.terminal_voltage = cur_emf - result.current * cur_r;
        result.power_load = result.terminal_voltage * result.current;
        result.power_loss = result.current * result.current * cur_r;
        result.reset_warning = (result.terminal_voltage < 2.85);

        const double discharged_ah = (result.current * dt_seconds) / 3600.0;
        params_.current_soc = std::max(0.0, params_.current_soc - (discharged_ah / params_.capacity_ah) * 100.0);

        return result;
    }

    [[nodiscard]] double soc() const noexcept { return params_.current_soc; }

private:
    BatteryParameters params_;
};

} // namespace power_system
