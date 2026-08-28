#include <stdio.h>
#include <math.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

typedef struct {
    double target_radius_m;
    double target_pull_rate_mps;
    double latent_heat_j_kg;
    double density_solid_kg_m3;
} ProcessParamsC;

typedef struct {
    ProcessParamsC params;
    double integral_err;
    double prev_err;
} CzochralskiControllerC;

typedef struct {
    double pull_rate_mps;
    double heater_power_kw;
} ControlOutputC;

void controller_init(CzochralskiControllerC *ctrl, ProcessParamsC params) {
    ctrl->params = params;
    ctrl->integral_err = 0.0;
    ctrl->prev_err = 0.0;
}

ControlOutputC controller_update(CzochralskiControllerC *ctrl, double measured_radius_m, double dt_sec) {
    double error = ctrl->params.target_radius_m - measured_radius_m;
    ctrl->integral_err += error * dt_sec;
    double derivative_err = (error - ctrl->prev_err) / dt_sec;
    ctrl->prev_err = error;

    double Kp_v = 3.0e-4;
    double Ki_v = 1.0e-5;
    double Kd_v = 5.0e-5;

    double delta_v = -(Kp_v * error + Ki_v * ctrl->integral_err + Kd_v * derivative_err);
    double pull_rate = ctrl->params.target_pull_rate_mps + delta_v;

    if (pull_rate < 0.33e-5) pull_rate = 0.33e-5;
    if (pull_rate > 6.67e-5) pull_rate = 6.67e-5;

    double Kp_p = 120.0;
    double heater_kw = 85.0 - Kp_p * error;
    if (heater_kw < 50.0) heater_kw = 50.0;
    if (heater_kw > 150.0) heater_kw = 150.0;

    ControlOutputC out = { pull_rate, heater_kw };
    return out;
}

int main(void) {
    ProcessParamsC params = { 0.150, 2.0e-5, 1.8e6, 2330.0 };
    CzochralskiControllerC ctrl;
    controller_init(&ctrl, params);

    printf("--- C Симуляція ПІД-контролера Чохральського ---\n");
    double radius = 0.142;
    double dt = 5.0;

    for (int step = 0; step <= 20; ++step) {
        double time_min = step * (dt / 60.0);
        ControlOutputC out = controller_update(&ctrl, radius, dt);

        printf("%.1f хв | Ø %.2f мм | v_p %.3f мм/хв | P %.1f кВт\n",
               time_min, radius * 2000.0, out.pull_rate_mps * 60000.0, out.heater_power_kw);

        radius += (params.target_pull_rate_mps - out.pull_rate_mps) * 0.05 * dt;
    }
    return 0;
}
