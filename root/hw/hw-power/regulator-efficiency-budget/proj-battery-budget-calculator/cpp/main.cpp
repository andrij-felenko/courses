#include <iostream>
#include <vector>
#include <string_view>
#include <span>
#include <chrono>
#include <cmath>
#include <iomanip>

enum class RegulatorType {
    LDO,
    BuckPFM,
    BuckPWM,
    BuckBoost4Switch
};

struct RegulatorModel {
    RegulatorType type;
    double iq_ua{1.0};           // Струм спокою, мкА
    double k_sw{0.04};           // Комутаційний коефіцієнт, Вт/А
    double r_eq{0.15};           // Еквівалентний опір силового контуру, Ом
    double p_fixed_pwm{0.015};   // Постійні комутаційні втрати PWM режиму, Вт

    [[nodiscard]] constexpr double loss(double v_in, double v_out, double i_out_a) const noexcept {
        const double iq_a = iq_ua * 1e-6;
        switch (type) {
            case RegulatorType::LDO:
                return (v_in - v_out) * i_out_a + v_in * iq_a;
            case RegulatorType::BuckPFM:
                return v_in * iq_a + k_sw * i_out_a + r_eq * i_out_a * i_out_a;
            case RegulatorType::BuckPWM:
                return p_fixed_pwm + k_sw * i_out_a + r_eq * i_out_a * i_out_a;
            case RegulatorType::BuckBoost4Switch:
                return v_in * iq_a + 1.8 * k_sw * i_out_a + 1.8 * r_eq * i_out_a * i_out_a;
        }
        return 0.0;
    }
};

struct LoadPhase {
    std::string_view name;
    std::chrono::milliseconds duration;
    double current_ma;
};

struct BatterySpec {
    double capacity_mah;
    double nominal_voltage;
    double usable_dod{0.90};
    double self_discharge_annual_pct{3.0};

    [[nodiscard]] double usable_energy_joules() const noexcept {
        return (capacity_mah * 1e-3) * nominal_voltage * 3600.0 * usable_dod;
    }
};

struct SimulationResult {
    double duration_s{0.0};
    double energy_out_joules{0.0};
    double energy_in_joules{0.0};
    double weighted_efficiency{0.0};
    double avg_current_in_ma{0.0};
    double peak_loss_power_watts{0.0};
    double autonomy_days{0.0};
    double autonomy_years{0.0};
};

class EnergyBudgetCalculator {
public:
    static SimulationResult run(std::span<const LoadPhase> profile,
                                const RegulatorModel& regulator,
                                double v_in, double v_out,
                                const BatterySpec& battery) {
        double total_dt_s = 0.0;
        double e_out = 0.0;
        double e_in = 0.0;
        double peak_loss = 0.0;

        for (const auto& phase : profile) {
            const double dt_s = phase.duration.count() * 1e-3;
            const double i_out_a = phase.current_ma * 1e-3;
            const double p_out = v_out * i_out_a;
            const double p_loss = regulator.loss(v_in, v_out, i_out_a);
            const double p_in = p_out + p_loss;

            if (p_loss > peak_loss) {
                peak_loss = p_loss;
            }

            e_out += p_out * dt_s;
            e_in += p_in * dt_s;
            total_dt_s += dt_s;
        }

        SimulationResult res{};
        if (total_dt_s <= 0.0 || e_in <= 0.0) {
            return res;
        }

        res.duration_s = total_dt_s;
        res.energy_out_joules = e_out;
        res.energy_in_joules = e_in;
        res.weighted_efficiency = e_out / e_in;
        res.peak_loss_power_watts = peak_loss;

        const double avg_power_in = e_in / total_dt_s;
        res.avg_current_in_ma = (avg_power_in / v_in) * 1e3;

        const double usable_joules = battery.usable_energy_joules();
        const double self_discharge_power = usable_joules * (battery.self_discharge_annual_pct * 0.01 / (365.25 * 86400.0));
        const double total_power_draw = avg_power_in + self_discharge_power;

        const double life_seconds = usable_joules / total_power_draw;
        res.autonomy_days = life_seconds / 86400.0;
        res.autonomy_years = res.autonomy_days / 365.25;

        return res;
    }
};

int main() {
    using namespace std::chrono_literals;

    const std::vector<LoadPhase> profile = {
        { "Deep Sleep",   9900ms,  0.015 },
        { "Sensor Read",    30ms,  4.500 },
        { "Compute Crypto", 20ms, 12.000 },
        { "Radio TX Burst", 50ms, 95.000 }
    };

    const BatterySpec li_ion{
        .capacity_mah = 1200.0,
        .nominal_voltage = 3.7,
        .usable_dod = 0.90,
        .self_discharge_annual_pct = 3.0
    };

    const RegulatorModel ldo_nano{
        .type = RegulatorType::LDO,
        .iq_ua = 0.8
    };

    const RegulatorModel buck_pfm{
        .type = RegulatorType::BuckPFM,
        .iq_ua = 2.0,
        .k_sw = 0.035,
        .r_eq = 0.18
    };

    const RegulatorModel buck_pwm{
        .type = RegulatorType::BuckPWM,
        .iq_ua = 15.0,
        .k_sw = 0.040,
        .r_eq = 0.18,
        .p_fixed_pwm = 0.015
    };

    constexpr double v_in = 3.7;
    constexpr double v_out = 3.3;

    std::cout << std::fixed << std::setprecision(2);
    std::cout << "=== СИМУЛЯЦІЯ ЕНЕРГЕТИЧНОГО БЮДЖЕТУ (C++20) ===\n\n";

    auto print_report = [](std::string_view label, const SimulationResult& r) {
        std::cout << label << "\n"
                  << "  Середньозважений ККД : " << r.weighted_efficiency * 100.0 << " %\n"
                  << "  Середній струм входу : " << std::setprecision(3) << r.avg_current_in_ma << " мА\n"
                  << "  Пікові втрати тепла  : " << std::setprecision(2) << r.peak_loss_power_watts * 1e3 << " мВт\n"
                  << "  Автономність         : " << r.autonomy_days << " днів (" << r.autonomy_years << " років)\n\n";
    };

    const auto r_ldo = EnergyBudgetCalculator::run(profile, ldo_nano, v_in, v_out, li_ion);
    print_report("[1] Нанопотужний LDO (Iq = 0.8 мкА):", r_ldo);

    const auto r_pfm = EnergyBudgetCalculator::run(profile, buck_pfm, v_in, v_out, li_ion);
    print_report("[2] Buck з підтримкою PFM (Iq = 2.0 мкА):", r_pfm);

    const auto r_pwm = EnergyBudgetCalculator::run(profile, buck_pwm, v_in, v_out, li_ion);
    print_report("[3] Класичний PWM Buck (P_fix = 15 мВт):", r_pwm);

    return 0;
}
