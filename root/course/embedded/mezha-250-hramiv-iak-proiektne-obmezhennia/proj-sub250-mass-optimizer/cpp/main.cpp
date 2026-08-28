#include <iostream>
#include <iomanip>
#include <string>
#include <string_view>
#include <vector>
#include <cmath>
#include <optional>
#include <algorithm>

constexpr double Sub250LimitGrams = 249.0;
constexpr int NumMotors = 4;

enum class BatteryChem {
    LiPo,
    LiIon
};

struct DryMassComponents {
    double frame_g{0.0};
    double aio_board_g{0.0};
    double motor_single_g{0.0};
    double props_set_g{0.0};
    double vtx_camera_g{0.0};
    double rx_antenna_g{0.0};
    double hardware_misc_g{0.0};

    [[nodiscard]] constexpr double total() const noexcept {
        return frame_g + aio_board_g + (motor_single_g * NumMotors) +
               props_set_g + vtx_camera_g + rx_antenna_g + hardware_misc_g;
    }
};

struct BatteryPack {
    std::string name;
    BatteryChem chem{BatteryChem::LiPo};
    int cells_s{4};
    double nominal_voltage_v{14.8};
    double capacity_mah{650.0};
    double pack_mass_g{114.0};
    double internal_resistance_mohm{24.0};
    double max_continuous_c{75.0};
};

struct PropulsionModel {
    double base_efficiency_gpw{6.2};
    double max_thrust_per_motor_g{340.0};
    double motor_resistance_mohm{120.0};
    double esc_mosfet_rds_mohm{4.5};
};

struct BuildAnalysisResult {
    double dry_mass_g{0.0};
    double all_up_weight_g{0.0};
    double mass_margin_g{0.0};
    bool is_sub250{false};
    double twr{0.0};
    double hover_thrust_per_motor_g{0.0};
    double hover_power_w{0.0};
    double hover_current_a{0.0};
    double loaded_voltage_v{0.0};
    double flight_time_minutes{0.0};
    double esc_channel_heat_loss_w{0.0};
    bool is_esc_safe{false};
};

class Sub250Optimizer {
public:
    [[nodiscard]] static std::optional<BuildAnalysisResult> analyze(
        const DryMassComponents& dry,
        const BatteryPack& bat,
        const PropulsionModel& prop,
        double avionics_power_w = 5.0,
        double esc_current_limit_a = 20.0) noexcept
    {
        const double m_dry = dry.total();
        const double auw = m_dry + bat.pack_mass_g;
        if (auw <= 0.0) return std::nullopt;

        BuildAnalysisResult res;
        res.dry_mass_g = m_dry;
        res.all_up_weight_g = auw;
        res.mass_margin_g = Sub250LimitGrams - auw;
        res.is_sub250 = (auw <= Sub250LimitGrams);

        const double max_total_thrust = prop.max_thrust_per_motor_g * NumMotors;
        res.twr = max_total_thrust / auw;

        const double hover_t_motor = auw / NumMotors;
        res.hover_thrust_per_motor_g = hover_t_motor;

        // Емпірична степенева крива деградації ККД пропелера від навантаження
        double eff_hover = prop.base_efficiency_gpw * std::pow(hover_t_motor / 50.0, -0.40);
        eff_hover = std::max(eff_hover, 2.0);

        const double p_mech_hover = auw / eff_hover;
        const double p_total_hover = p_mech_hover + avionics_power_w;
        res.hover_power_w = p_total_hover;

        const double r_total = (bat.internal_resistance_mohm + 15.0) / 1000.0;
        const double v_ocv = bat.nominal_voltage_v;
        double v_load = v_ocv;
        double i_hover = 0.0;

        for (int iter = 0; iter < 5; ++iter) {
            i_hover = p_total_hover / v_load;
            v_load = v_ocv - (i_hover * r_total);
            if (v_load < (bat.cells_s * 2.8)) {
                v_load = bat.cells_s * 2.8;
                break;
            }
        }

        res.hover_current_a = i_hover;
        res.loaded_voltage_v = v_load;

        const double usable_cap_ah = (bat.capacity_mah / 1000.0) * 0.85;
        res.flight_time_minutes = (usable_cap_ah / i_hover) * 60.0;

        const double i_channel = i_hover / NumMotors;
        const double r_fet = prop.esc_mosfet_rds_mohm / 1000.0;
        res.esc_channel_heat_loss_w = (i_channel * i_channel) * r_fet;

        const double max_ch_current = (max_total_thrust / (prop.base_efficiency_gpw * 0.5)) / (v_load * NumMotors);
        res.is_esc_safe = (max_ch_current <= esc_current_limit_a);

        return res;
    }

    static void print_report(std::string_view build_name, const BuildAnalysisResult& res) {
        std::cout << "====================================================\n";
        std::cout << "ЗБІРКА: " << build_name << "\n";
        std::cout << "====================================================\n";
        std::cout << std::fixed << std::setprecision(1);
        std::cout << "Суха маса апарата:    " << std::setw(6) << res.dry_mass_g << " г\n";
        std::cout << "Повна злітна маса:    " << std::setw(6) << res.all_up_weight_g << " г  ["
                  << (res.is_sub250 ? "SUB-250G OK" : "ПЕРЕВИЩЕННЯ МЕЖІ!")
                  << ", запас: " << std::showpos << res.mass_margin_g << std::noshowpos << " г]\n";
        std::cout << std::setprecision(2);
        std::cout << "Коефіцієнт TWR:       " << std::setw(6) << res.twr << " : 1\n";
        std::cout << std::setprecision(1);
        std::cout << "Тяга на мотор (hover):" << std::setw(6) << res.hover_thrust_per_motor_g << " г\n";
        std::cout << "Потужність висіння:   " << std::setw(6) << res.hover_power_w << " Вт\n";
        std::cout << std::setprecision(2);
        std::cout << "Струм висіння:        " << std::setw(6) << res.hover_current_a
                  << " А (напруга під навант.: " << res.loaded_voltage_v << " В)\n";
        std::cout << std::setprecision(1);
        std::cout << "Очікуваний час польоту: " << std::setw(4) << res.flight_time_minutes << " хв\n";
        std::cout << std::setprecision(3);
        std::cout << "Втрати FET ESC (канал): " << std::setw(5) << res.esc_channel_heat_loss_w << " Вт  ["
                  << (res.is_esc_safe ? "ESC безпечний" : "УВАГА: перевантаження ESC!") << "]\n";
        std::cout << "----------------------------------------------------\n\n";
    }
};

int main() {
    const DryMassComponents freestyle_dry{
        .frame_g = 42.0,
        .aio_board_g = 8.5,
        .motor_single_g = 9.5,
        .props_set_g = 12.0,
        .vtx_camera_g = 34.0,
        .rx_antenna_g = 2.2,
        .hardware_misc_g = 6.0
    };

    const BatteryPack lipo_4s{
        .name = "Tattu R-Line 4S 650mAh 75C",
        .chem = BatteryChem::LiPo,
        .cells_s = 4,
        .nominal_voltage_v = 14.8,
        .capacity_mah = 650.0,
        .pack_mass_g = 114.0,
        .internal_resistance_mohm = 24.0,
        .max_continuous_c = 75.0
    };

    const PropulsionModel prop_3in{
        .base_efficiency_gpw = 6.2,
        .max_thrust_per_motor_g = 340.0,
        .motor_resistance_mohm = 120.0,
        .esc_mosfet_rds_mohm = 4.5
    };

    if (auto res = Sub250Optimizer::analyze(freestyle_dry, lipo_4s, prop_3in, 6.0, 20.0)) {
        Sub250Optimizer::print_report("3-inch Micro Freestyle (DJI O3 HD + 4S LiPo)", *res);
    }

    const DryMassComponents lr_dry{
        .frame_g = 24.0,
        .aio_board_g = 6.8,
        .motor_single_g = 8.5,
        .props_set_g = 8.0,
        .vtx_camera_g = 12.0,
        .rx_antenna_g = 1.5,
        .hardware_misc_g = 3.5
    };

    const BatteryPack liion_2s{
        .name = "Custom 2S 18650 3500mAh 10C",
        .chem = BatteryChem::LiIon,
        .cells_s = 2,
        .nominal_voltage_v = 7.4,
        .capacity_mah = 3500.0,
        .pack_mass_g = 164.0,
        .internal_resistance_mohm = 55.0,
        .max_continuous_c = 10.0
    };

    const PropulsionModel prop_4in{
        .base_efficiency_gpw = 9.8,
        .max_thrust_per_motor_g = 175.0,
        .motor_resistance_mohm = 180.0,
        .esc_mosfet_rds_mohm = 4.5
    };

    if (auto res = Sub250Optimizer::analyze(lr_dry, liion_2s, prop_4in, 4.0, 12.0)) {
        Sub250Optimizer::print_report("4-inch Long Range Ultralight (Analog + 2S Li-Ion)", *res);
    }

    return 0;
}
