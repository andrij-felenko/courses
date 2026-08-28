/**
 * @file helmholtz_dsp.h
 * @brief C API заголовочний контракт для акустичного розрахунку резонатора Гельмгольца.
 */

#ifndef HELMHOLTZ_DSP_H
#define HELMHOLTZ_DSP_H

#ifdef __cplusplus
extern "C" {
#endif

#include <stddef.h>
#include <stdbool.h>

typedef enum {
    HELMHOLTZ_OK = 0,
    HELMHOLTZ_ERR_INVALID_PARAM = -1,
    HELMHOLTZ_ERR_WAVELENGTH_VIOLATION = -2,
    HELMHOLTZ_ERR_SHORT_NECK_VIOLATION = -3,
    HELMHOLTZ_ERR_NONLINEAR_REGIME = -4
} helmholtz_status_t;

typedef struct {
    double cavity_volume_m3;
    double neck_length_m;
    double neck_radius_m;
    double temperature_celsius;
    double static_pressure_pa;
    bool is_flanged_inner;
    bool is_flanged_outer;
} helmholtz_config_t;

typedef struct {
    double resonance_freq_hz;
    double effective_length_m;
    double acoustic_mass_kg_m4;
    double compliance_m5_N;
    double quality_factor_q;
    double max_valid_freq_hz;
} helmholtz_metrics_t;

void helmholtz_config_init_default(helmholtz_config_t* cfg);
helmholtz_status_t helmholtz_compute_metrics(const helmholtz_config_t* cfg, helmholtz_metrics_t* metrics);
helmholtz_status_t helmholtz_get_impedance(const helmholtz_config_t* cfg, const helmholtz_metrics_t* metrics, double freq_hz, double* out_real_ra, double* out_imag_xa);
helmholtz_status_t helmholtz_get_absorption_coefficient(const helmholtz_config_t* cfg, const helmholtz_metrics_t* metrics, double pipe_area_m2, double freq_hz, double* out_alpha);

#ifdef __cplusplus
}
#endif

#endif /* HELMHOLTZ_DSP_H */
