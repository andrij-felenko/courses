#include <stdbool.h>
#include <math.h>

typedef enum {
    THERMAL_STATE_NORMAL = 0,
    THERMAL_STATE_THROTTLING,
    THERMAL_STATE_CRITICAL
} thermal_state_t;

typedef struct {
    float r_w;        // Активний опір обмотки (Ом)
    float r_th;       // Тепловий опір (К/Вт)
    float tau;        // Теплова часова константа (с)
    float t_amb;      // Температура довкілля (°C)
    float t_warn;     // Поріг початку тротлінгу (°C)
    float t_crit;     // Поріг критичного вимкнення (°C)
    float i_nom;      // Номінальний струм (А)
} thermal_config_t;

typedef struct {
    thermal_config_t cfg;
    float t_est;
    thermal_state_t state;
} thermal_estimator_t;

void thermal_estimator_init(thermal_estimator_t *est, const thermal_config_t *cfg) {
    est->cfg = *cfg;
    est->t_est = cfg->t_amb;
    est->state = THERMAL_STATE_NORMAL;
}

void thermal_estimator_update(thermal_estimator_t *est, float i_phase_rms, float dt) {
    float p_loss = i_phase_rms * i_phase_rms * est->cfg.r_w;
    float t_target = p_loss * est->cfg.r_th;
    float dt_est = ((t_target - (est->t_est - est->cfg.t_amb)) / est->cfg.tau) * dt;
    est->t_est += dt_est;

    if (est->t_est >= est->cfg.t_crit) {
        est->state = THERMAL_STATE_CRITICAL;
    } else if (est->t_est >= est->cfg.t_warn) {
        est->state = THERMAL_STATE_THROTTLING;
    } else {
        est->state = THERMAL_STATE_NORMAL;
    }
}

float thermal_estimator_get_current_limit(const thermal_estimator_t *est) {
    if (est->state == THERMAL_STATE_CRITICAL) {
        return 0.0f;
    }
    if (est->state == THERMAL_STATE_THROTTLING) {
        float scale = 1.0f - (est->t_est - est->cfg.t_warn) / (est->cfg.t_crit - est->cfg.t_warn);
        if (scale < 0.0f) scale = 0.0f;
        return est->cfg.i_nom * scale;
    }
    return est->cfg.i_nom;
}
