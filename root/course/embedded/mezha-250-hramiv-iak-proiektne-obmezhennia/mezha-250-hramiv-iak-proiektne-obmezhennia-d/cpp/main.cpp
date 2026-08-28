#include <iostream>
#include <iomanip>
#include <cmath>
#include <optional>

constexpr double MaxAuwSub250 = 249.0;

struct Sub250Config {
    double frame_weight_g{0.0};
    double aio_weight_g{0.0};
    double four_motors_weight_g{0.0};
    double vtx_cam_rx_weight_g{0.0};
    double props_and_screws_g{0.0};
    double battery_weight_g{0.0};
    double battery_capacity_mah{0.0};
    double battery_voltage_nom_v{14.8};
    double battery_esr_mohm{25.0};
    double base_efficiency_gpw{7.5};
};

struct Sub250Report {
    double total_mass_g{0.0};
    bool is_legal_sub250{false};
    double hover_power_watts{0.0};
    double hover_current_amps{0.0};
    double loaded_voltage_v{0.0};
    double flight_time_min{0.0};
};

[[nodiscard]] constexpr std::optional<Sub250Report> evaluate_sub250_build(const Sub250Config& cfg) noexcept {
    Sub250Report rep;
    rep.total_mass_g = cfg.frame_weight_g + cfg.aio_weight_g +
                       cfg.four_motors_weight_g + cfg.vtx_cam_rx_weight_g +
                       cfg.props_and_screws_g + cfg.battery_weight_g;

    if (rep.total_mass_g <= 0.0) return std::nullopt;

    rep.is_legal_sub250 = (rep.total_mass_g <= MaxAuwSub250);

    const double hover_thrust_per_motor = rep.total_mass_g / 4.0;
    const double eff = cfg.base_efficiency_gpw * std::pow(hover_thrust_per_motor / 60.0, -0.38);
    rep.hover_power_watts = rep.total_mass_g / eff + 4.5;

    const double r_loop = (cfg.battery_esr_mohm + 18.0) / 1000.0;
    double v_load = cfg.battery_voltage_nom_v;
    double i_current = 0.0;

    for (int i = 0; i < 4; ++i) {
        i_current = rep.hover_power_watts / v_load;
        v_load = cfg.battery_voltage_nom_v - (i_current * r_loop);
    }

    rep.hover_current_amps = i_current;
    rep.loaded_voltage_v = v_load;

    const double usable_cap_ah = (cfg.battery_capacity_mah / 1000.0) * 0.85;
    rep.flight_time_min = (usable_cap_ah / i_current) * 60.0;

    return rep;
}
