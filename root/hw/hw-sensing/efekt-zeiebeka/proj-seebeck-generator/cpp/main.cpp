#include <iostream>
#include <array>
#include <cmath>
#include <iomanip>
#include <span>
#include <string_view>

namespace thermo {

/* Фізичні параметри напівпровідникового модуля TEG */
struct TegProperties {
    double seebeck_p{210e-6};     // В/К для p-гілки
    double seebeck_n{-210e-6};    // В/К для n-гілки
    double resistivity_p{1.2e-5}; // Ом·м
    double resistivity_n{1.2e-5}; // Ом·м
    double thermal_cond_p{1.5};   // Вт/(м·К)
    double thermal_cond_n{1.5};   // Вт/(м·К)
    double leg_length{1.5e-3};    // висота стовпчика, м
    double leg_area{1.96e-6};     // площа перерізу, м² (1.4 × 1.4 мм)
    std::size_t couples_count{127};
};

/* Стан генератора під навантаженням */
struct GeneratorResult {
    double open_circuit_voltage{};
    double internal_resistance{};
    double thermal_conductance{};
    double load_current{};
    double load_voltage{};
    double electrical_power{};
    double heat_absorbed_hot{};
    double heat_rejected_cold{};
    double efficiency_percent{};
};

class ThermoelectricGenerator {
public:
    explicit constexpr ThermoelectricGenerator(TegProperties params) noexcept
        : params_(params) {}

    [[nodiscard]] GeneratorResult simulate(double temp_hot_k, double temp_cold_k, double load_res_ohm) const noexcept {
        GeneratorResult res{};
        const double delta_t = temp_hot_k - temp_cold_k;
        const double total_seebeck = (params_.seebeck_p - params_.seebeck_n) * static_cast<double>(params_.couples_count);
        const double geom_factor = params_.leg_length / params_.leg_area;

        res.open_circuit_voltage = total_seebeck * delta_t;
        res.internal_resistance = (params_.resistivity_p + params_.resistivity_n) * geom_factor * static_cast<double>(params_.couples_count);
        res.thermal_conductance = (params_.thermal_cond_p + params_.thermal_cond_n) * (1.0 / geom_factor) * static_cast<double>(params_.couples_count);

        const double total_circuit_r = res.internal_resistance + load_res_ohm;
        res.load_current = (total_circuit_r > 1e-12) ? (res.open_circuit_voltage / total_circuit_r) : 0.0;
        res.load_voltage = res.load_current * load_res_ohm;
        res.electrical_power = res.load_current * res.load_current * load_res_ohm;

        // Потоки тепла Пельтьє, кондуктивного витоку та внутрішнього самонагріву
        const double q_peltier_hot = total_seebeck * temp_hot_k * res.load_current;
        const double q_conduction = res.thermal_conductance * delta_t;
        const double q_joule_half = 0.5 * res.load_current * res.load_current * res.internal_resistance;

        res.heat_absorbed_hot = q_peltier_hot + q_conduction - q_joule_half;
        res.heat_rejected_cold = (total_seebeck * temp_cold_k * res.load_current) + q_conduction + q_joule_half;

        res.efficiency_percent = (res.heat_absorbed_hot > 1e-9)
            ? (res.electrical_power / res.heat_absorbed_hot) * 100.0
            : 0.0;

        return res;
    }

private:
    TegProperties params_;
};

/* ──────────────── Прецизійна лінеаризація термопари типу K за ITS-90 ─────────────── */

class TypeKThermocouple {
public:
    static constexpr std::array<double, 10> k_poly_t_to_v{
        -1.76004136860E-01,
         3.89212049750E+01,
         1.85587700320E-02,
        -9.94575928740E-05,
         3.18409457190E-07,
        -5.60728448890E-10,
         5.60750590590E-13,
        -3.20207200030E-16,
         9.71511471520E-20,
        -1.21047212750E-23
    };

    static constexpr std::array<double, 10> k_poly_v_to_t{
         0.0000000E+00,
         2.5083550E+01,
         7.8601060E-02,
        -2.5031310E-01,
         8.3152700E-02,
        -1.2280340E-02,
         9.8040360E-04,
        -4.4130300E-05,
         1.0577340E-06,
        -1.0527550E-08
    };

    [[nodiscard]] static double temperature_to_microvolts(double temp_celsius) noexcept {
        double uv = k_poly_t_to_v.back();
        for (auto it = k_poly_t_to_v.rbegin() + 1; it != k_poly_t_to_v.rend(); ++it) {
            uv = uv * temp_celsius + *it;
        }
        constexpr double a0 = 1.185976e+02;
        constexpr double a1 = -1.183432e-04;
        constexpr double a2 = 1.269686e+02;
        uv += a0 * std::exp(a1 * (temp_celsius - a2) * (temp_celsius - a2));
        return uv;
    }

    [[nodiscard]] static double millivolts_to_temperature(double emf_millivolts) noexcept {
        double temp = k_poly_v_to_t.back();
        for (auto it = k_poly_v_to_t.rbegin() + 1; it != k_poly_v_to_t.rend(); ++it) {
            temp = temp * emf_millivolts + *it;
        }
        return temp;
    }

    [[nodiscard]] static double calculate_hot_junction(double raw_measured_uv, double cold_junction_temp_c) noexcept {
        const double cjc_equivalent_uv = temperature_to_microvolts(cold_junction_temp_c);
        const double compensated_total_uv = raw_measured_uv + cjc_equivalent_uv;
        return millivolts_to_temperature(compensated_total_uv * 1e-3);
    }
};

} // namespace thermo

int main() {
    using namespace thermo;

    const ThermoelectricGenerator teg{TegProperties{}};
    constexpr double th = 473.15; // 200 °C
    constexpr double tc = 303.15; // 30 °C

    const auto probe = teg.simulate(th, tc, 1.0);
    const auto matched_op = teg.simulate(th, tc, probe.internal_resistance);

    std::cout << std::fixed << std::setprecision(3);
    std::cout << "=== C++20 Модель термоелектричного генератора (TEG) ===\n";
    std::cout << "Перепад температур: " << (th - tc) << " K\n";
    std::cout << "ЕРС холостого ходу V_oc: " << matched_op.open_circuit_voltage << " В\n";
    std::cout << "Внутрішній опір R_int: " << matched_op.internal_resistance << " Ом\n";
    std::cout << "Струм при узгодженні I: " << matched_op.load_current << " А\n";
    std::cout << "Вихідна електрична потужність: " << matched_op.electrical_power << " Вт\n";
    std::cout << "Термоелектричний ККД: " << std::setprecision(2) << matched_op.efficiency_percent << " %\n\n";

    constexpr double cjc_temp = 24.5;
    constexpr double measured_sensor_uv = 12150.0;
    const double object_temp = TypeKThermocouple::calculate_hot_junction(measured_sensor_uv, cjc_temp);

    std::cout << "=== Прецизійна лінеаризація Type K (ITS-90) ===\n";
    std::cout << "Температура плати CJC: " << cjc_temp << " °C\n";
    std::cout << "Виміряний сигнал на вході АЦП: " << measured_sensor_uv << " мкВ\n";
    std::cout << "Дійсна температура гарячого спаю: " << object_temp << " °C\n";

    return 0;
}
