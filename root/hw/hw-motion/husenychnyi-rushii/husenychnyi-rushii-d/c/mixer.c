/* mixer.h та mixer.c — алгоритм керування гусеничним шасі на чистому C */
#include <math.h>
#include <stdbool.h>

typedef struct {
    float left;   /* Нормалізована швидкість лівої гусениці [-1.0 ... +1.0] */
    float right;  /* Нормалізована швидкість правої гусениці [-1.0 ... +1.0] */
} TrackVelocities;

typedef struct {
    float max_accel;       /* Максимальне прискорення (одиниць/сек), наприклад 2.5 */
    float current_limit_a; /* Поріг обмеження струму (А), наприклад 40.0 */
    float left_filtered;   /* Поточний стан фільтра лівого борту */
    float right_filtered;  /* Поточний стан фільтра правого борту */
} SkidMixer;

void skid_mixer_init(SkidMixer* mixer, float max_accel, float current_limit_a) {
    mixer->max_accel = max_accel;
    mixer->current_limit_a = current_limit_a;
    mixer->left_filtered = 0.0f;
    mixer->right_filtered = 0.0f;
}

static float clamp_f(float val, float min_v, float max_v) {
    if (val < min_v) return min_v;
    if (val > max_v) return max_v;
    return val;
}

TrackVelocities skid_mixer_update(SkidMixer* mixer,
                                  float throttle,
                                  float steering,
                                  float measured_current_a,
                                  float dt) {
    /* 1. Обмеження вхідних сигналів діапазоном [-1.0, 1.0] */
    throttle = clamp_f(throttle, -1.0f, 1.0f);
    steering = clamp_f(steering, -1.0f, 1.0f);

    /* 2. Розрахунок сирих швидкостей */
    float v_left = throttle + steering;
    float v_right = throttle - steering;

    /* 3. Масштабування з пріоритетом повороту (Turn-Priority Anti-Saturation) */
    float max_mag = fmaxf(fabsf(v_left), fabsf(v_right));
    if (max_mag > 1.0f) {
        v_left /= max_mag;
        v_right /= max_mag;
    }

    /* 4. Захисний струмовий/тепловий троттлінг */
    if (measured_current_a > mixer->current_limit_a) {
        float over_current = measured_current_a - mixer->current_limit_a;
        float derating = 1.0f - clamp_f(over_current / 15.0f, 0.0f, 0.75f);
        v_left *= derating;
        v_right *= derating;
    }

    /* 5. Обмеження темпу наростання швидкості (Slew Rate Limiter) */
    float max_delta = mixer->max_accel * dt;
    
    float delta_left = v_left - mixer->left_filtered;
    delta_left = clamp_f(delta_left, -max_delta, max_delta);
    mixer->left_filtered += delta_left;

    float delta_right = v_right - mixer->right_filtered;
    delta_right = clamp_f(delta_right, -max_delta, max_delta);
    mixer->right_filtered += delta_right;

    TrackVelocities out;
    out.left = mixer->left_filtered;
    out.right = mixer->right_filtered;
    return out;
}
