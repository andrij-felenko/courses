#include <stdio.h>
#include <math.h>

#define MAGNUS_A 6.112
#define MAGNUS_B 17.67
#define MAGNUS_C 243.5
#define PSYCHRO_A 0.000662

typedef struct {
    double relative_humidity_pct;
    double actual_vapor_pressure_hpa;
    double saturation_vapor_pressure_hpa;
    double dew_point_celsius;
} humidity_result_t;

// Обчислення тиску насиченої пари (гПа)
double calc_saturation_vapor_pressure(double temp_celsius) {
    return MAGNUS_A * exp((MAGNUS_B * temp_celsius) / (MAGNUS_C + temp_celsius));
}

// Розрахунок точки роси (°C)
double calc_dew_point(double temp_celsius, double rh_pct) {
    if (rh_pct <= 0.0) return -999.0;
    double gamma = log(rh_pct / 100.0) + (MAGNUS_B * temp_celsius) / (MAGNUS_C + temp_celsius);
    return (MAGNUS_C * gamma) / (MAGNUS_B - gamma);
}

// Повний психрометричний розрахунок
int calc_psychrometric_data(double t_dry, double t_wet, double pressure_hpa, humidity_result_t *out_res) {
    if (!out_res || t_wet > t_dry) return -1;

    double e_s_wet = calc_saturation_vapor_pressure(t_wet);
    double e_s_dry = calc_saturation_vapor_pressure(t_dry);
    double e_actual = e_s_wet - PSYCHRO_A * pressure_hpa * (t_dry - t_wet);

    double rh = (e_actual / e_s_dry) * 100.0;
    if (rh < 0.0) rh = 0.0;
    if (rh > 100.0) rh = 100.0;

    out_res->relative_humidity_pct = rh;
    out_res->actual_vapor_pressure_hpa = e_actual;
    out_res->saturation_vapor_pressure_hpa = e_s_dry;
    out_res->dew_point_celsius = calc_dew_point(t_dry, rh);

    return 0;
}

int main(void) {
    humidity_result_t res;
    double t_dry = 25.0;
    double t_wet = 18.5;
    double pressure = 1013.25;

    if (calc_psychrometric_data(t_dry, t_wet, pressure, &res) == 0) {
        printf("Психрометрія (C): T_dry = %.1f C, T_wet = %.1f C\n", t_dry, t_wet);
        printf("  RH = %.2f %%\n", res.relative_humidity_pct);
        printf("  e  = %.2f hPa (e_s = %.2f hPa)\n", res.actual_vapor_pressure_hpa, res.saturation_vapor_pressure_hpa);
        printf("  Td = %.2f C\n", res.dew_point_celsius);
    }
    return 0;
}
