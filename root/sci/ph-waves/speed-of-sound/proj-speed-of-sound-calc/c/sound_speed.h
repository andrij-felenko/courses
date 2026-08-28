/* sound_speed.h - C99 API for acoustic speed calculation */
#ifndef SOUND_SPEED_H
#define SOUND_SPEED_H

#include <stdbool.h>
#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef enum {
    SOUND_OK = 0,
    SOUND_ERR_INVALID_PARAM = -1,
    SOUND_ERR_TEMP_OUT_OF_RANGE = -2,
    SOUND_ERR_PRESSURE_INVALID = -3
} sound_status_t;

typedef struct {
    double temperature_c;  /* Temperature in degrees Celsius [-40..+60] */
    double relative_humidity_pct; /* Relative humidity [0..100%] */
    double pressure_pa;    /* Barometric pressure in Pa (e.g. 101325.0) */
} air_params_t;

typedef struct {
    double temperature_c;  /* Water temperature [0..35 °C] */
    double salinity_ppt;   /* Salinity in parts per thousand (‰) [0..40] */
    double depth_m;        /* Depth in meters [0..8000] */
} water_params_t;

typedef struct {
    double young_modulus_pa; /* Young's modulus E in Pa */
    double poisson_ratio;    /* Poisson's ratio nu [0..0.49] */
    double density_kg_m3;    /* Density rho in kg/m^3 */
} solid_params_t;

typedef struct {
    double longitudinal_m_s; /* Speed of longitudinal wave c_L */
    double transverse_m_s;   /* Speed of transverse wave c_S (0 for fluids) */
} sound_speed_result_t;

/* Calculate speed of sound in humid air */
sound_status_t calc_sound_speed_air(const air_params_t* params, double* out_speed_m_s);

/* Calculate speed of sound in water (Medwin formula) */
sound_status_t calc_sound_speed_water(const water_params_t* params, double* out_speed_m_s);

/* Calculate longitudinal and transverse speed in isotropic solid */
sound_status_t calc_sound_speed_solid(const solid_params_t* params, sound_speed_result_t* out_result);

#ifdef __cplusplus
}
#endif

#endif /* SOUND_SPEED_H */

/* sound_speed.c - Implementation */
#include <math.h>

static double calc_saturation_vapor_pressure(double t_c) {
    /* Antoine equation approximation for water vapor pressure in Pa */
    return 610.78 * exp((17.27 * t_c) / (t_c + 237.3));
}

sound_status_t calc_sound_speed_air(const air_params_t* params, double* out_speed_m_s) {
    if (!params || !out_speed_m_s) return SOUND_ERR_INVALID_PARAM;
    if (params->temperature_c < -50.0 || params->temperature_c > 80.0) return SOUND_ERR_TEMP_OUT_OF_RANGE;
    if (params->pressure_pa <= 1000.0) return SOUND_ERR_PRESSURE_INVALID;

    double t = params->temperature_c;
    double rh = params->relative_humidity_pct;
    if (rh < 0.0) rh = 0.0;
    if (rh > 100.0) rh = 100.0;

    /* Saturated vapor pressure */
    double p_sat = calc_saturation_vapor_pressure(t);
    double p_v = (rh / 100.0) * p_sat;

    /* Speed of sound calculation considering humidity density correction */
    double c_dry = 331.3 * sqrt(1.0 + t / 273.15);
    /* Vapor correction factor */
    double mole_fraction_v = p_v / params->pressure_pa;
    double speed = c_dry * (1.0 + 0.16 * mole_fraction_v);

    *out_speed_m_s = speed;
    return SOUND_OK;
}

sound_status_t calc_sound_speed_water(const water_params_t* params, double* out_speed_m_s) {
    if (!params || !out_speed_m_s) return SOUND_ERR_INVALID_PARAM;
    double t = params->temperature_c;
    double s = params->salinity_ppt;
    double z = params->depth_m;

    if (t < -2.0 || t > 40.0) return SOUND_ERR_TEMP_OUT_OF_RANGE;

    /* Medwin empirical formula for sound speed in sea water */
    double c = 1449.2 + (4.6 * t) - (0.055 * t * t) + (0.00029 * t * t * t)
               + (1.34 - 0.01 * t) * (s - 35.0) + (0.016 * z);

    *out_speed_m_s = c;
    return SOUND_OK;
}

sound_status_t calc_sound_speed_solid(const solid_params_t* params, sound_speed_result_t* out_result) {
    if (!params || !out_result) return SOUND_ERR_INVALID_PARAM;
    if (params->young_modulus_pa <= 0.0 || params->density_kg_m3 <= 0.0) return SOUND_ERR_INVALID_PARAM;
    if (params->poisson_ratio < 0.0 || params->poisson_ratio >= 0.499) return SOUND_ERR_INVALID_PARAM;

    double e = params->young_modulus_pa;
    double nu = params->poisson_ratio;
    double rho = params->density_kg_m3;

    /* Longitudinal speed c_L */
    double c_L = sqrt((e * (1.0 - nu)) / (rho * (1.0 + nu) * (1.0 - 2.0 * nu)));
    /* Transverse speed c_S */
    double c_S = sqrt(e / (2.0 * rho * (1.0 + nu)));

    out_result->longitudinal_m_s = c_L;
    out_result->transverse_m_s = c_S;
    return SOUND_OK;
}
