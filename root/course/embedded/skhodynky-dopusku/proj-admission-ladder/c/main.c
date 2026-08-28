#include <stdint.h>
#include <stdbool.h>
#include <math.h>

#define ADMISSION_BLEND_TIME_MS      200
#define ADMISSION_DEADMAN_TIMEOUT_MS 300
#define ADMISSION_SUGGESTION_TTL_MS  1500
#define ADMISSION_STICK_TAKEOVER_THR 0.15f

typedef enum {
    MODE_SHADOW = 0,
    MODE_ADVISORY,
    MODE_SUPERVISED,
    MODE_BOUNDED_AUTONOMOUS,
    MODE_MANUAL_OVERRIDE,
    MODE_FAILSAFE_RTH
} admission_mode_t;

typedef struct {
    float roll_deg;      /* Крен: -45.0 .. +45.0 */
    float pitch_deg;     /* Тангаж: -45.0 .. +45.0 */
    float yaw_rate_dps;  /* Кутова швидкість рискання: град/с */
    float throttle_norm; /* Тяга: 0.0 .. 1.0 */
} setpoint_t;

typedef struct {
    float distance_to_fence_m;
    float wind_speed_mps;
    float ekf_pos_uncertainty_m;
    bool  link_alive;
    bool  deadman_pressed;
    bool  suggestion_ack_button;
} telemetry_state_t;

typedef struct {
    admission_mode_t current_mode;
    admission_mode_t target_mode;
    setpoint_t       last_active_setpoint;
    uint32_t         mode_enter_timestamp_ms;
    uint32_t         last_deadman_ping_ms;
    uint32_t         suggestion_timestamp_ms;
    bool             has_pending_suggestion;
    float            blend_progress; /* 0.0 -> 1.0 */
    float            shadow_divergence_accum;
    uint32_t         shadow_sample_count;
} admission_arbiter_t;

void arbiter_init(admission_arbiter_t *arb, admission_mode_t initial_mode) {
    arb->current_mode = initial_mode;
    arb->target_mode = initial_mode;
    arb->last_active_setpoint = (setpoint_t){0.0f, 0.0f, 0.0f, 0.0f};
    arb->mode_enter_timestamp_ms = 0;
    arb->last_deadman_ping_ms = 0;
    arb->suggestion_timestamp_ms = 0;
    arb->has_pending_suggestion = false;
    arb->blend_progress = 1.0f;
    arb->shadow_divergence_accum = 0.0f;
    arb->shadow_sample_count = 0;
}

static bool check_stick_deflection(const setpoint_t *pilot) {
    return (fabsf(pilot->roll_deg) > ADMISSION_STICK_TAKEOVER_THR * 45.0f) ||
           (fabsf(pilot->pitch_deg) > ADMISSION_STICK_TAKEOVER_THR * 45.0f);
}

static setpoint_t blend_setpoints(const setpoint_t *from, const setpoint_t *to, float alpha) {
    if (alpha >= 1.0f) return *to;
    if (alpha <= 0.0f) return *from;
    
    setpoint_t res;
    res.roll_deg      = from->roll_deg      + alpha * (to->roll_deg      - from->roll_deg);
    res.pitch_deg     = from->pitch_deg     + alpha * (to->pitch_deg     - from->pitch_deg);
    res.yaw_rate_dps  = from->yaw_rate_dps  + alpha * (to->yaw_rate_dps  - from->yaw_rate_dps);
    res.throttle_norm = from->throttle_norm + alpha * (to->throttle_norm - from->throttle_norm);
    return res;
}

setpoint_t arbiter_update(admission_arbiter_t *arb,
                          const setpoint_t *pilot_sp,
                          const setpoint_t *algo_sp,
                          const telemetry_state_t *telem,
                          uint32_t now_ms)
{
    setpoint_t target_sp;

    /* 1. Оновлення таймера утримання кнопки аварійного переривання */
    if (telem->deadman_pressed) {
        arb->last_deadman_ping_ms = now_ms;
    }

    /* 2. Обробка переходів скінченного автомата */
    switch (arb->current_mode) {
        case MODE_SHADOW:
            /* Повне керування у пілота; уставка алгоритму йде в аналізатор */
            target_sp = *pilot_sp;
            {
                float d_roll = pilot_sp->roll_deg - algo_sp->roll_deg;
                float d_pitch = pilot_sp->pitch_deg - algo_sp->pitch_deg;
                float err = sqrtf(d_roll * d_roll + d_pitch * d_pitch);
                arb->shadow_divergence_accum += err;
                arb->shadow_sample_count++;
            }
            break;

        case MODE_ADVISORY:
            target_sp = *pilot_sp;
            if (arb->has_pending_suggestion) {
                if (now_ms - arb->suggestion_timestamp_ms > ADMISSION_SUGGESTION_TTL_MS) {
                    /* Застаріла підказка анулюється */
                    arb->has_pending_suggestion = false;
                } else if (telem->suggestion_ack_button) {
                    /* Оператор підтвердив маневр */
                    target_sp = *algo_sp;
                    arb->has_pending_suggestion = false;
                }
            }
            break;

        case MODE_SUPERVISED:
            /* Перевірка сигналу перехоплення або відпускання dead man's switch */
            if (!telem->deadman_pressed || check_stick_deflection(pilot_sp)) {
                arb->current_mode = MODE_MANUAL_OVERRIDE;
                arb->blend_progress = 0.0f;
                target_sp = *pilot_sp;
            } else {
                target_sp = *algo_sp;
            }
            break;

        case MODE_BOUNDED_AUTONOMOUS:
            /* Перевірка виходу за межі робочого домену (ODD) */
            if (telem->distance_to_fence_m < 15.0f ||
                telem->wind_speed_mps > 12.0f ||
                telem->ekf_pos_uncertainty_m > 2.5f ||
                !telem->link_alive)
            {
                arb->current_mode = MODE_FAILSAFE_RTH;
                arb->blend_progress = 0.0f;
                target_sp = *pilot_sp; /* RTH логіка підмінить уставку */
            } else if (check_stick_deflection(pilot_sp)) {
                /* Екстрене перехоплення стіком пілота */
                arb->current_mode = MODE_MANUAL_OVERRIDE;
                arb->blend_progress = 0.0f;
                target_sp = *pilot_sp;
            } else {
                target_sp = *algo_sp;
            }
            break;

        case MODE_MANUAL_OVERRIDE:
            target_sp = *pilot_sp;
            break;

        case MODE_FAILSAFE_RTH:
        default:
            target_sp = *pilot_sp;
            break;
    }

    /* 3. Безривкове змішування уставок (Bumpless Transfer) */
    if (arb->blend_progress < 1.0f) {
        float dt_ratio = 20.0f / (float)ADMISSION_BLEND_TIME_MS; /* Крок 20 мс */
        arb->blend_progress += dt_ratio;
        if (arb->blend_progress > 1.0f) arb->blend_progress = 1.0f;
        
        target_sp = blend_setpoints(&arb->last_active_setpoint, &target_sp, arb->blend_progress);
    }

    arb->last_active_setpoint = target_sp;
    return target_sp;
}
