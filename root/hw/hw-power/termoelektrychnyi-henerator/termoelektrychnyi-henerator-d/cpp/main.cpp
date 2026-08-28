#include <cmath>
#include <optional>
#include <algorithm>

// Фізичні та конструктивні параметри ТЕГ модуля
struct TegSpecs {
    int couples{127};              // Кількість пар термопар
    double seebeck_couple{400e-6}; // Коефіцієнт Зеєбека пари (В/К)
    double r_internal{2.4};        // Внутрішній електричний опір (Ом)
    double theta_module{1.8};      // Тепловий опір модуля (К/Вт)
    double theta_hot_contact{0.3}; // Опір гарячого контакту (К/Вт)
    double theta_heatsink{2.5};    // Опір радіатора (К/Вт)

    [[nodiscard]] constexpr double total_thermal_resistance() const noexcept {
        return theta_hot_contact + theta_module + theta_heatsink;
    }

    [[nodiscard]] constexpr double seebeck_total() const noexcept {
        return couples * seebeck_couple;
    }
};

// Звіт про робочу точку системи
struct TegOperatingPoint {
    double q_heat_flow_w{0.0};
    double delta_t_module_k{0.0};
    double v_open_circuit_v{0.0};
    double v_mpp_v{0.0};
    double i_mpp_a{0.0};
    double p_max_w{0.0};
    double efficiency_pct{0.0};
};

class ThermoelectricModel {
public:
    explicit constexpr ThermoelectricModel(TegSpecs specs) noexcept 
        : specs_(specs) {}

    [[nodiscard]] TegOperatingPoint evaluate(double t_source_c, double t_ambient_c) const noexcept {
        const double delta_t_sys = t_source_c - t_ambient_c;
        if (delta_t_sys <= 0.0) {
            return TegOperatingPoint{};
        }

        const double theta_tot = specs_.total_thermal_resistance();
        const double q_heat = delta_t_sys / theta_tot;
        const double dt_teg = q_heat * specs_.theta_module;

        const double voc = specs_.seebeck_total() * dt_teg;
        const double v_mpp = voc * 0.5;
        const double i_mpp = v_mpp / specs_.r_internal;
        const double p_max = (voc * voc) / (4.0 * specs_.r_internal);
        const double eff = (q_heat > 0.0) ? (p_max / q_heat) * 100.0 : 0.0;

        return TegOperatingPoint{
            .q_heat_flow_w = q_heat,
            .delta_t_module_k = dt_teg,
            .v_open_circuit_v = voc,
            .v_mpp_v = v_mpp,
            .i_mpp_a = i_mpp,
            .p_max_w = p_max,
            .efficiency_pct = eff
        };
    }

private:
    TegSpecs specs_;
};
