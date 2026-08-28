/*
 * charge_relaxation_api.h — C API для розрахунку параметрів релаксації заряду
 */

#ifndef CHARGE_RELAXATION_API_H
#define CHARGE_RELAXATION_API_H

#ifdef __cplusplus
extern "C" {
#endif

#define CR_EPS0 8.854187817e-12

typedef enum {
    CR_SUCCESS = 0,
    CR_ERR_INVALID_PARAM = -1,
    CR_ERR_ZERO_CONDUCTIVITY = -2
} cr_status_t;

typedef struct {
    double rel_permittivity; /* εr */
    double conductivity;     /* σ (См/м) */
} cr_material_t;

typedef struct {
    double tau_maxwell;       /* τ_m (с) */
    double half_life;         /* t_1/2 (с) */
    double decay_99_percent;  /* t_99% (с) */
} cr_relaxation_result_t;

typedef struct {
    double tau_mw;            /* τ_MW (с) */
    double steady_state_sigma;/* σ_f(∞) (Кл/м²) */
} cr_maxwell_wagner_result_t;

/* Обчислення максвеллівського часу релаксації для одного середовища */
cr_status_t cr_calculate_relaxation(
    const cr_material_t *mat,
    cr_relaxation_result_t *res
);

/* Розрахунок часу спаду напруги ESD від V_initial до V_target */
cr_status_t cr_calculate_esd_decay_time(
    const cr_material_t *mat,
    double v_initial,
    double v_target,
    double *decay_time_seconds
);

/* Розрахунок параметрів міжфазної релаксації Максвелла-Вагнера для 2 шарів */
cr_status_t cr_calculate_maxwell_wagner(
    const cr_material_t *mat1, double thickness1,
    const cr_material_t *mat2, double thickness2,
    double applied_voltage,
    cr_maxwell_wagner_result_t *res
);

#ifdef __cplusplus
}
#endif

#endif /* CHARGE_RELAXATION_API_H */
