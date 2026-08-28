#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <stdbool.h>

#define GRAVITY 9.80665
#define WATER_DENSITY 998.2
#define WATER_KINEMATIC_VISCOSITY 1.004e-6

typedef struct {
    double depth_h1;
    double depth_h2;
    double velocity_v1;
    double velocity_v2;
    double froude_Fr1;
    double froude_Fr2;
    double energy_loss_dE;
    bool is_valid_jump;
} hydraulic_jump_res_t;

typedef struct {
    double model_length;
    double model_speed;
    double model_Fr;
    double model_Re;
    double ship_speed_knots;
    double ship_speed_ms;
    double ship_Re;
    double drag_wave_N;
    double drag_total_ship_N;
    double power_kw;
} ship_scaling_res_t;

hydraulic_jump_res_t calculate_hydraulic_jump(double discharge_q, double h1) {
    hydraulic_jump_res_t res = {0};
    if (h1 <= 0.0 || discharge_q <= 0.0) {
        return res;
    }

    res.depth_h1 = h1;
    res.velocity_v1 = discharge_q / h1;
    res.froude_Fr1 = res.velocity_v1 / sqrt(GRAVITY * h1);

    if (res.froude_Fr1 <= 1.0) {
        res.is_valid_jump = false;
        return res;
    }

    res.is_valid_jump = true;
    double fr1_sq = res.froude_Fr1 * res.froude_Fr1;
    res.depth_h2 = 0.5 * h1 * (sqrt(1.0 + 8.0 * fr1_sq) - 1.0);
    res.velocity_v2 = discharge_q / res.depth_h2;
    res.froude_Fr2 = res.velocity_v2 / sqrt(GRAVITY * res.depth_h2);

    double dh = res.depth_h2 - res.depth_h1;
    res.energy_loss_dE = (dh * dh * dh) / (4.0 * res.depth_h1 * res.depth_h2);

    return res;
}

double calculate_ittc_cf(double reynolds) {
    if (reynolds <= 0.0) return 0.0;
    double log_re = log10(reynolds);
    double denominator = log_re - 2.0;
    return 0.075 / (denominator * denominator);
}

ship_scaling_res_t scale_ship_model(double L_ship, double L_model, double v_ship_knots, 
                                     double S_ship, double R_total_model_N) {
    ship_scaling_res_t res = {0};
    double scale = L_ship / L_model;

    res.ship_speed_knots = v_ship_knots;
    res.ship_speed_ms = v_ship_knots * 0.514444;
    res.model_length = L_model;
    res.model_speed = res.ship_speed_ms / sqrt(scale);

    res.model_Fr = res.model_speed / sqrt(GRAVITY * L_model);
    res.model_Re = (res.model_speed * L_model) / WATER_KINEMATIC_VISCOSITY;
    res.ship_Re = (res.ship_speed_ms * L_ship) / WATER_KINEMATIC_VISCOSITY;

    double S_model = S_ship / (scale * scale);
    double q_model = 0.5 * WATER_DENSITY * res.model_speed * res.model_speed;
    double C_total_model = R_total_model_N / (q_model * S_model);

    double C_friction_model = calculate_ittc_cf(res.model_Re);
    double C_wave = C_total_model - C_friction_model;
    if (C_wave < 0.0) C_wave = 0.0;

    double C_friction_ship = calculate_ittc_cf(res.ship_Re);
    double C_total_ship = C_wave + C_friction_ship;

    double q_ship = 0.5 * WATER_DENSITY * res.ship_speed_ms * res.ship_speed_ms;
    res.drag_total_ship_N = C_total_ship * q_ship * S_ship;
    res.drag_wave_N = C_wave * q_ship * S_ship;
    res.power_kw = (res.drag_total_ship_N * res.ship_speed_ms) / 1000.0;

    return res;
}

int main(void) {
    printf("=== Симуляція гідравлічного стрибка ===\n");
    double q = 3.5; // витрата на м ширини (м²/с)
    double h1 = 0.4; // вхідна глибина (м)
    hydraulic_jump_res_t jump = calculate_hydraulic_jump(q, h1);

    if (jump.is_valid_jump) {
        printf("Fr1: %.3f (бурхливий) -> h1: %.3f м, v1: %.2f м/с\n", jump.froude_Fr1, jump.depth_h1, jump.velocity_v1);
        printf("Fr2: %.3f (спокійний) -> h2: %.3f м, v2: %.2f м/с\n", jump.froude_Fr2, jump.depth_h2, jump.velocity_v2);
        printf("Втрата енергії dE: %.4f м вод. ст.\n", jump.energy_loss_dE);
    } else {
        printf("Гідравлічний стрибок відсутній: Fr1 <= 1.0\n");
    }

    printf("\n=== Масштабування судна за Фрудом (ITTC-1957) ===\n");
    double L_s = 120.0; // довжина судна, м
    double L_m = 4.0;   // довжина моделі, м
    double v_s = 20.0;  // швидкість судна, вузлів
    double S_s = 2200.0;// площа поверхні судна, м²
    double R_m = 25.5;  // виміряний опір моделі, Н

    ship_scaling_res_t ship = scale_ship_model(L_s, L_m, v_s, S_s, R_m);
    printf("Масштаб lambda: %.1f\n", L_s / L_m);
    printf("Швидкість моделі v_m: %.3f м/с (Fr = %.3f)\n", ship.model_speed, ship.model_Fr);
    printf("Re моделі: %.2e, Re судна: %.2e\n", ship.model_Re, ship.ship_Re);
    printf("Прогнозований повний опір судна: %.2f кН\n", ship.drag_total_ship_N / 1000.0);
    printf("Необхідна потужність буксирування: %.2f кВт\n", ship.power_kw);

    return 0;
}
