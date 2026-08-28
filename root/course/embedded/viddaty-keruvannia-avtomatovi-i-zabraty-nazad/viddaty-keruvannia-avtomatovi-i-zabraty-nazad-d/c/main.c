#include <stdint.h>
#include <stdbool.h>
#include <math.h>

#define STICK_DEADBAND_NORM    0.12f   /* Поріг відхилення стіка: 12% */
#define BLEND_IN_TIME_SEC      0.20f   /* Час переходу в ручний: 200 мс */
#define BLEND_OUT_TIME_SEC     0.40f   /* Час повернення в авто: 400 мс */
#define HANDBACK_HOLD_SEC      1.50f   /* Час утримання нейтралі: 1.5 с */

typedef enum {
    TAKEOVER_STATE_AUTO_NAV = 0,
    TAKEOVER_STATE_OVERRIDE_IN,
    TAKEOVER_STATE_MANUAL_HOLD,
    TAKEOVER_STATE_HANDBACK_WAIT,
    TAKEOVER_STATE_BLENDING_OUT
} takeover_state_t;

typedef struct {
    float roll;      /* Нормалізовані значення від -1.0 до +1.0 */
    float pitch;
    float yaw;
    float throttle; /* Нормалізоване від 0.0 до 1.0 (або від -1 до +1) */
} stick_input_t;

typedef struct {
    float roll;      /* Сигнали уставки (кути або моменти) */
    float pitch;
    float yaw;
    float throttle;
} control_command_t;

typedef struct {
    takeover_state_t state;
    float alpha;               /* Поточний коефіцієнт змішування [0.0 ... 1.0] */
    float hold_timer_sec;      /* Лічильник часу утримання в нейтралі */
    bool override_annunciation;/* Прапорець для відправки події в MAVLink */
} takeover_controller_t;

void takeover_init(takeover_controller_t *ctrl) {
    if (!ctrl) return;
    ctrl->state = TAKEOVER_STATE_AUTO_NAV;
    ctrl->alpha = 0.0f;
    ctrl->hold_timer_sec = 0.0f;
    ctrl->override_annunciation = false;
}

static bool check_stick_deflection(const stick_input_t *sticks) {
    /* Перевіряємо перевищення порогу по будь-якій із основних осей */
    if (fabsf(sticks->roll) > STICK_DEADBAND_NORM) return true;
    if (fabsf(sticks->pitch) > STICK_DEADBAND_NORM) return true;
    if (fabsf(sticks->yaw) > STICK_DEADBAND_NORM) return true;
    
    /* Для газу перевіряємо відхилення від середнього положення зависання (0.5) */
    if (fabsf(sticks->throttle - 0.5f) > STICK_DEADBAND_NORM) return true;

    return false;
}

void takeover_update(takeover_controller_t *ctrl,
                     const stick_input_t *sticks,
                     const control_command_t *cmd_auto,
                     const control_command_t *cmd_pilot,
                     control_command_t *cmd_out,
                     float dt_sec) {
    if (!ctrl || !sticks || !cmd_auto || !cmd_pilot || !cmd_out) return;

    bool sticks_deflected = check_stick_deflection(sticks);

    switch (ctrl->state) {
        case TAKEOVER_STATE_AUTO_NAV:
            ctrl->alpha = 0.0f;
            if (sticks_deflected) {
                ctrl->state = TAKEOVER_STATE_OVERRIDE_IN;
                ctrl->override_annunciation = true;
            }
            break;

        case TAKEOVER_STATE_OVERRIDE_IN:
            /* Лінійне наростання ваги оператора */
            ctrl->alpha += dt_sec / BLEND_IN_TIME_SEC;
            if (ctrl->alpha >= 1.0f) {
                ctrl->alpha = 1.0f;
                ctrl->state = TAKEOVER_STATE_MANUAL_HOLD;
            }
            break;

        case TAKEOVER_STATE_MANUAL_HOLD:
            ctrl->alpha = 1.0f;
            if (!sticks_deflected) {
                ctrl->state = TAKEOVER_STATE_HANDBACK_WAIT;
                ctrl->hold_timer_sec = 0.0f;
            }
            break;

        case TAKEOVER_STATE_HANDBACK_WAIT:
            ctrl->alpha = 1.0f;
            if (sticks_deflected) {
                /* Пілот знову втрутився до завершення таймауту */
                ctrl->state = TAKEOVER_STATE_MANUAL_HOLD;
                ctrl->hold_timer_sec = 0.0f;
            } else {
                ctrl->hold_timer_sec += dt_sec;
                if (ctrl->hold_timer_sec >= HANDBACK_HOLD_SEC) {
                    ctrl->state = TAKEOVER_STATE_BLENDING_OUT;
                }
            }
            break;

        case TAKEOVER_STATE_BLENDING_OUT:
            if (sticks_deflected) {
                /* Миттєве повторне перехоплення під час повернення в авто */
                ctrl->state = TAKEOVER_STATE_OVERRIDE_IN;
            } else {
                ctrl->alpha -= dt_sec / BLEND_OUT_TIME_SEC;
                if (ctrl->alpha <= 0.0f) {
                    ctrl->alpha = 0.0f;
                    ctrl->state = TAKEOVER_STATE_AUTO_NAV;
                }
            }
            break;
    }

    /* Обчислення підсумкових команд: u = (1 - α) * u_auto + α * u_pilot */
    const float a = ctrl->alpha;
    const float inv_a = 1.0f - a;

    cmd_out->roll     = inv_a * cmd_auto->roll     + a * cmd_pilot->roll;
    cmd_out->pitch    = inv_a * cmd_auto->pitch    + a * cmd_pilot->pitch;
    cmd_out->yaw      = inv_a * cmd_auto->yaw      + a * cmd_pilot->yaw;
    cmd_out->throttle = inv_a * cmd_auto->throttle + a * cmd_pilot->throttle;
}
