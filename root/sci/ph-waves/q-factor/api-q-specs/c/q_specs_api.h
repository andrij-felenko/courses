/* q_specs_api.h — Специфікація типів та API розрахунку добротності */
#ifndef Q_SPECS_API_H
#define Q_SPECS_API_H

#include <stddef.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef enum {
    Q_DOMAIN_MECHANICAL,   /* Маса, жорсткість, демпфер */
    Q_DOMAIN_ELECTRICAL_SERIES,  /* Послідовний RLC */
    Q_DOMAIN_ELECTRICAL_PARALLEL,/* Паралельний RLC */
    Q_DOMAIN_ACOUSTIC_MEMBRANE,  /* Акустичний резонатор */
    Q_DOMAIN_OPTICAL_CAVITY      /* Оптичний резонатор */
} q_domain_t;

typedef enum {
    Q_STATUS_OK = 0,
    Q_STATUS_INVALID_PARAM = -1,
    Q_STATUS_OVERDAMPED = -2,    /* Q < 0.5, коливань немає */
    Q_STATUS_NONLINEAR = -3
} q_status_t;

/* Вхідні параметри для механічного осцилятора */
typedef struct {
    double mass_kg;
    double stiffness_nm;
    double damping_c_nsm;
} q_mech_params_t;

/* Вхідні параметри для електричного контуру */
typedef struct {
    double resistance_ohm;
    double inductance_henry;
    double capacitance_farad;
} q_el_params_t;

/* Результат розрахунку добротності */
typedef struct {
    double q_factor;
    double f0_hz;
    double bandwidth_3db_hz;
    double damping_ratio_zeta;
    double decay_time_tau_sec;
    q_status_t status;
} q_result_t;

/* Публічні функції API */
q_status_t q_calc_mechanical(const q_mech_params_t *params, q_result_t *out_result);
q_status_t q_calc_electrical_series(const q_el_params_t *params, q_result_t *out_result);
q_status_t q_calc_electrical_parallel(const q_el_params_t *params, q_result_t *out_result);
q_status_t q_calc_from_energy(double w_stored_joules, double w_lost_per_cycle_joules, double f0_hz, q_result_t *out_result);

#ifdef __cplusplus
}
#endif

#endif /* Q_SPECS_API_H */
