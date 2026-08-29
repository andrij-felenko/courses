#include "ahrs.h"

#include <stddef.h>

void ahrs_init(ahrs_t *f, float kp, float ki, bool coning_enabled) {
    if (!f) return;
    f->q = quat_identity();
    f->gyro_bias = vec3_zero();
    f->delta_theta = vec3_zero();
    f->prev_delta = vec3_zero();
    f->coning = vec3_zero();
    f->fast_steps = 0;
    f->kp = kp;
    f->ki = ki;
    f->accel_gate = 0.10f;
    f->coning_enabled = coning_enabled;
    f->accel_rejected = 0;
    f->faults = 0;
}

void ahrs_push_gyro(ahrs_t *f, vec3_t omega_body, float dt) {
    if (!f) return;
    if (!vec3_is_finite(omega_body) || !(dt > 0.0f) || !isfinite(dt)) {
        f->faults++;      /* битий кадр IMU не рухає стан: краще пропустити такт, ніж отруїти оцінку */
        return;
    }
    vec3_t corrected = vec3_sub(omega_body, f->gyro_bias);
    vec3_t d = vec3_scale(corrected, dt);
    if (f->coning_enabled && f->fast_steps > 0) {
        /* Δθ_coning = 0.5·(Δθ_{k−1} × Δθ_k): те, що втрачає просте підсумовування. */
        f->coning = vec3_add(f->coning, vec3_scale(vec3_cross(f->prev_delta, d), 0.5f));
    }
    f->prev_delta = d;
    f->delta_theta = vec3_add(f->delta_theta, d);
    f->fast_steps++;
}

void ahrs_update(ahrs_t *f, const vec3_t *accel_body, float dt) {
    if (!f || !(dt > 0.0f) || !isfinite(dt)) return;

    vec3_t phi = vec3_add(f->delta_theta, f->coning);
    f->delta_theta = vec3_zero();
    f->coning = vec3_zero();
    f->prev_delta = vec3_zero();
    f->fast_steps = 0;

    if (accel_body && vec3_is_finite(*accel_body)) {
        vec3_t a_hat;
        float n = vec3_norm(*accel_body);
        bool trusted = vec3_normalize(*accel_body, &a_hat) &&
                       fabsf(n - AHRS_GRAVITY) <= f->accel_gate * AHRS_GRAVITY;
        if (trusted) {
            /* Куди «низ» дивиться за поточною оцінкою, у осях тіла. */
            vec3_t down_body = quat_rotate_inv(f->q, vec3_make(0.0f, 0.0f, 1.0f));
            /* Векторний добуток виміряного й очікуваного напрямку — кут неузгодження. */
            vec3_t err = vec3_cross(a_hat, down_body);
            phi = vec3_add(phi, vec3_scale(err, f->kp * dt));
            /* Стала складова неузгодження — це і є зсув нуля гіроскопа. */
            f->gyro_bias = vec3_sub(f->gyro_bias, vec3_scale(err, f->ki * dt));
        } else {
            /* Апарат розганяється: питома сила вже не гравітація, вертикалі з неї не взяти. */
            f->accel_rejected++;
        }
    }

    f->q = quat_normalize(quat_mul(f->q, quat_from_rotation_vector(phi)));
    if (!quat_is_finite(f->q)) {
        f->q = quat_identity();
        f->gyro_bias = vec3_zero();
        f->faults++;
    }
}

euler_t ahrs_euler(const ahrs_t *f) {
    if (!f) {
        euler_t z = { 0.0f, 0.0f, 0.0f };
        return z;
    }
    return quat_to_euler(f->q);
}
