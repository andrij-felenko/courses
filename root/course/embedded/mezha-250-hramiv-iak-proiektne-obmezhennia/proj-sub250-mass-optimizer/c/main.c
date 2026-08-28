#include <stdio.h>
#include <stdbool.h>
#include <math.h>

#define SUB250_LIMIT_GRAMS 249.0
#define NUM_MOTORS 4

typedef enum {
    BATTERY_CHEM_LIPO,
    BATTERY_CHEM_LIION
} BatteryChem;

typedef struct {
    double frame_g;
    double aio_board_g;
    double motor_single_g;
    double props_set_g;
    double vtx_camera_g;
    double rx_antenna_g;
    double hardware_misc_g;
} DryMassComponents;

typedef struct {
    const char* name;
    BatteryChem chem;
    int cells_s;
    double nominal_voltage_v;
    double capacity_mah;
    double pack_mass_g;
    double internal_resistance_mohm;
    double max_continuous_c;
} BatteryPack;

typedef struct {
    double base_efficiency_gpw; // г/Вт при 50 г тяги
    double max_thrust_per_motor_g;
    double motor_resistance_mohm;
    double esc_mosfet_rds_mohm;
} PropulsionModel;

typedef struct {
    double dry_mass_g;
    double all_up_weight_g;
    double mass_margin_g;
    bool is_sub250;
    double twr;
    double hover_thrust_per_motor_g;
    double hover_power_w;
    double hover_current_a;
    double loaded_voltage_v;
    double flight_time_minutes;
    double esc_channel_heat_loss_w;
    bool is_esc_safe;
} BuildAnalysisResult;

static double calculate_dry_mass(const DryMassComponents* dry) {
    return dry->frame_g + dry->aio_board_g + (dry->motor_single_g * NUM_MOTORS) +
           dry->props_set_g + dry->vtx_camera_g + dry->rx_antenna_g + dry->hardware_misc_g;
}

static bool analyze_sub250_build(
    const DryMassComponents* dry,
    const BatteryPack* bat,
    const PropulsionModel* prop,
    double avionics_power_w,
    double esc_current_limit_a,
    BuildAnalysisResult* out_result)
{
    if (!dry || !bat || !prop || !out_result) return false;

    double m_dry = calculate_dry_mass(dry);
    double auw = m_dry + bat->pack_mass_g;

    out_result->dry_mass_g = m_dry;
    out_result->all_up_weight_g = auw;
    out_result->mass_margin_g = SUB250_LIMIT_GRAMS - auw;
    out_result->is_sub250 = (auw <= SUB250_LIMIT_GRAMS);

    double max_total_thrust = prop->max_thrust_per_motor_g * NUM_MOTORS;
    out_result->twr = max_total_thrust / auw;

    double hover_t_per_motor = auw / NUM_MOTORS;
    out_result->hover_thrust_per_motor_g = hover_t_per_motor;

    // Степенева апроксимація ефективності: eff = eff_base * (T / 50)^(-0.4)
    double eff_hover = prop->base_efficiency_gpw * pow(hover_t_per_motor / 50.0, -0.40);
    if (eff_hover < 2.0) eff_hover = 2.0;

    double p_mechanical_hover = auw / eff_hover;
    double p_total_hover = p_mechanical_hover + avionics_power_w;
    out_result->hover_power_w = p_total_hover;

    // Ітераційне визначення робочої напруги з урахуванням внутрішнього опору
    double r_total_ohm = (bat->internal_resistance_mohm + 15.0) / 1000.0; // +15 мОм роз'єм/провід
    double v_ocv = bat->nominal_voltage_v;
    double v_load = v_ocv;
    double i_hover = 0.0;

    for (int iter = 0; iter < 5; ++iter) {
        i_hover = p_total_hover / v_load;
        v_load = v_ocv - (i_hover * r_total_ohm);
        if (v_load < (bat->cells_s * 2.8)) {
            v_load = bat->cells_s * 2.8;
            break;
        }
    }

    out_result->hover_current_a = i_hover;
    out_result->loaded_voltage_v = v_load;

    // Розрахунок часу висіння (85% корисної ємності)
    double usable_cap_ah = (bat->capacity_mah / 1000.0) * 0.85;
    out_result->flight_time_minutes = (usable_cap_ah / i_hover) * 60.0;

    // Оцінка нагріву ключа ESC на канал
    double i_channel = i_hover / NUM_MOTORS;
    double r_fet = prop->esc_mosfet_rds_mohm / 1000.0;
    out_result->esc_channel_heat_loss_w = (i_channel * i_channel) * r_fet;

    double max_channel_current = (max_total_thrust / (prop->base_efficiency_gpw * 0.5)) / (v_load * NUM_MOTORS);
    out_result->is_esc_safe = (max_channel_current <= esc_current_limit_a);

    return true;
}

void print_report(const char* build_name, const BuildAnalysisResult* res) {
    printf("====================================================\n");
    printf("ЗБІРКА: %s\n", build_name);
    printf("====================================================\n");
    printf("Суха маса апарата:    %6.1f г\n", res->dry_mass_g);
    printf("Повна злітна маса:    %6.1f г  [%s, запас: %+5.1f г]\n",
           res->all_up_weight_g,
           res->is_sub250 ? "SUB-250G OK" : "ПЕРЕВИЩЕННЯ МЕЖІ!",
           res->mass_margin_g);
    printf("Коефіцієнт TWR:       %6.2f : 1\n", res->twr);
    printf("Тяга на мотор (hover):%6.1f г\n", res->hover_thrust_per_motor_g);
    printf("Потужність висіння:   %6.1f Вт\n", res->hover_power_w);
    printf("Струм висіння:        %6.2f А (напруга під навант.: %.2f В)\n",
           res->hover_current_a, res->loaded_voltage_v);
    printf("Очікуваний час польоту: %4.1f хв\n", res->flight_time_minutes);
    printf("Втрати FET ESC (канал): %5.3f Вт  [%s]\n",
           res->esc_channel_heat_loss_w,
           res->is_esc_safe ? "ESC безпечний" : "УВАГА: перевантаження ESC!");
    printf("----------------------------------------------------\n\n");
}

int main(void) {
    DryMassComponents micro_freestyle_dry = {
        .frame_g = 42.0,
        .aio_board_g = 8.5,
        .motor_single_g = 9.5,
        .props_set_g = 12.0,
        .vtx_camera_g = 34.0,
        .rx_antenna_g = 2.2,
        .hardware_misc_g = 6.0
    };

    BatteryPack lipo_4s = {
        .name = "Tattu R-Line 4S 650mAh 75C",
        .chem = BATTERY_CHEM_LIPO,
        .cells_s = 4,
        .nominal_voltage_v = 14.8,
        .capacity_mah = 650.0,
        .pack_mass_g = 114.0,
        .internal_resistance_mohm = 24.0,
        .max_continuous_c = 75.0
    };

    PropulsionModel prop_3inch = {
        .base_efficiency_gpw = 6.2,
        .max_thrust_per_motor_g = 340.0,
        .motor_resistance_mohm = 120.0,
        .esc_mosfet_rds_mohm = 4.5
    };

    BuildAnalysisResult res1;
    analyze_sub250_build(&micro_freestyle_dry, &lipo_4s, &prop_3inch, 6.0, 20.0, &res1);
    print_report("3-inch Micro Freestyle (DJI O3 HD + 4S LiPo)", &res1);

    DryMassComponents ultralight_lr_dry = {
        .frame_g = 24.0,
        .aio_board_g = 6.8,
        .motor_single_g = 8.5,
        .props_set_g = 8.0,
        .vtx_camera_g = 12.0,
        .rx_antenna_g = 1.5,
        .hardware_misc_g = 3.5
    };

    BatteryPack liion_2s = {
        .name = "Custom 2S 18650 3500mAh 10C",
        .chem = BATTERY_CHEM_LIION,
        .cells_s = 2,
        .nominal_voltage_v = 7.4,
        .capacity_mah = 3500.0,
        .pack_mass_g = 164.0,
        .internal_resistance_mohm = 55.0,
        .max_continuous_c = 10.0
    };

    PropulsionModel prop_4inch = {
        .base_efficiency_gpw = 9.8,
        .max_thrust_per_motor_g = 175.0,
        .motor_resistance_mohm = 180.0,
        .esc_mosfet_rds_mohm = 4.5
    };

    BuildAnalysisResult res2;
    analyze_sub250_build(&ultralight_lr_dry, &liion_2s, &prop_4inch, 4.0, 12.0, &res2);
    print_report("4-inch Long Range Ultralight (Analog + 2S Li-Ion)", &res2);

    return 0;
}
