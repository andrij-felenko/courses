#include <stdbool.h>
#include <math.h>

typedef struct {
    float vx;       /* м/с */
    float yaw_rate; /* рад/с */
} ControlSetpoint;

typedef struct {
    float range_ahead_m;
    float max_brake_accel_mps2;
    float safety_margin_m;
    float loop_dt_sec;
} DynamicObstacleEnvelope;

/* Детермінований бар'єр безпеки гальмівного шляху: O(1), без виділення пам'яті */
ControlSetpoint apply_stopping_barrier(
    ControlSetpoint candidate,
    const DynamicObstacleEnvelope *env,
    bool *was_clamped
) {
    ControlSetpoint safe = candidate;
    *was_clamped = false;

    if (safe.vx <= 0.0f) {
        return safe; /* Рух назад або стоп перешкодою спереду не обмежується */
    }

    /* Доступна дистанція до фізичного контакту з урахуванням запасу */
    float d_avail = env->range_ahead_m - env->safety_margin_m;
    if (d_avail <= 0.0f) {
        safe.vx = 0.0f;
        *was_clamped = true;
        return safe;
    }

    /* Максимальна швидкість, з якої апарат гарантовано зупиниться: v = sqrt(2 * a * d) */
    float v_max_allowed = sqrtf(2.0f * env->max_brake_accel_mps2 * d_avail);

    if (safe.vx > v_max_allowed) {
        safe.vx = v_max_allowed;
        *was_clamped = true;
    }

    return safe;
}
