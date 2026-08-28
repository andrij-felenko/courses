#include <stdio.h>
#include <stdbool.h>
#include <math.h>

#define MAX_AUW_SUB250 249.0

typedef struct {
    double frame_weight_g;
    double aio_weight_g;
    double four_motors_weight_g;
    double vtx_cam_rx_weight_g;
    double props_and_screws_g;
    double battery_weight_g;
    double battery_capacity_mah;
    double battery_voltage_nom_v;
    double battery_esr_mohm;
    double base_efficiency_gpw; // г/Вт при навантаженні 60 г/мотор
} Sub250Config;

typedef struct {
    double total_mass_g;
    bool is_legal_sub250;
    double hover_power_watts;
    double hover_current_amps;
    double loaded_voltage_v;
    double flight_time_min;
} Sub250Report;

bool evaluate_sub250_build(const Sub250Config* cfg, Sub250Report* rep) {
    if (!cfg || !rep) return false;

    rep->total_mass_g = cfg->frame_weight_g + cfg->aio_weight_g +
                        cfg->four_motors_weight_g + cfg->vtx_cam_rx_weight_g +
                        cfg->props_and_screws_g + cfg->battery_weight_g;

    rep->is_legal_sub250 = (rep->total_mass_g <= MAX_AUW_SUB250);

    // Розрахунок механічної потужності висіння
    double hover_thrust_per_motor = rep->total_mass_g / 4.0;
    double eff = cfg->base_efficiency_gpw * pow(hover_thrust_per_motor / 60.0, -0.38);
    rep->hover_power_watts = rep->total_mass_g / eff + 4.5; // +4.5 Вт бортова електроніка

    // Ітераційне визначення робочої напруги
    double r_loop = (cfg->battery_esr_mohm + 18.0) / 1000.0; // внутрішній опір + опір роз'єму XT30
    double v_load = cfg->battery_voltage_nom_v;
    double i_current = 0.0;

    for (int i = 0; i < 4; ++i) {
        i_current = rep->hover_power_watts / v_load;
        v_load = cfg->battery_voltage_nom_v - (i_current * r_loop);
    }

    rep->hover_current_amps = i_current;
    rep->loaded_voltage_v = v_load;

    // Час польоту з урахуванням 85% корисної ємності розряду
    double usable_cap_ah = (cfg->battery_capacity_mah / 1000.0) * 0.85;
    rep->flight_time_min = (usable_cap_ah / i_current) * 60.0;

    return true;
}
