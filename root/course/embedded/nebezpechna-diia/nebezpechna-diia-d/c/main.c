#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

// Магічні токени безпеки (захист від затирання пам'яті)
#define SAFETY_TOKEN_DISARMED   0x0000U
#define SAFETY_TOKEN_ARMED      0x5A5AU
#define SAFETY_TOKEN_EXECUTE    0xA5A5U

typedef enum {
    INTERLOCK_STATE_SAFE_IDLE = 0,
    INTERLOCK_STATE_ARMED_LATCH,
    INTERLOCK_STATE_HOLD_PROGRESS,
    INTERLOCK_STATE_COUNTDOWN_GRACE,
    INTERLOCK_STATE_TRIGGERED,
    INTERLOCK_STATE_ABORTED
} InterlockState_t;

typedef struct {
    uint32_t arm_window_ms;       // Максимальний час зведення (наприклад, 5000 мс)
    uint32_t hold_required_ms;    // Необхідний час утримання кнопки (наприклад, 3000 мс)
    uint32_t grace_countdown_ms;  // Вікно скасування перед спуском (наприклад, 2000 мс)
    void (*on_action_execute)(void);
    void (*on_state_change)(InterlockState_t new_state);
} InterlockConfig_t;

typedef struct {
    InterlockState_t state;
    uint16_t auth_token;
    uint32_t timer_ms;
    uint32_t hold_accum_ms;
    bool is_button_pressed;
    InterlockConfig_t config;
} SafetyInterlock_t;

void SafetyInterlock_Init(SafetyInterlock_t *inst, const InterlockConfig_t *cfg) {
    if (!inst || !cfg) return;
    inst->state = INTERLOCK_STATE_SAFE_IDLE;
    inst->auth_token = SAFETY_TOKEN_DISARMED;
    inst->timer_ms = 0;
    inst->hold_accum_ms = 0;
    inst->is_button_pressed = false;
    inst->config = *cfg;
}

void SafetyInterlock_Arm(SafetyInterlock_t *inst) {
    if (!inst) return;
    if (inst->state == INTERLOCK_STATE_SAFE_IDLE) {
        inst->state = INTERLOCK_STATE_ARMED_LATCH;
        inst->auth_token = SAFETY_TOKEN_ARMED;
        inst->timer_ms = inst->config.arm_window_ms;
        inst->hold_accum_ms = 0;
        if (inst->config.on_state_change) {
            inst->config.on_state_change(inst->state);
        }
    }
}

void SafetyInterlock_Abort(SafetyInterlock_t *inst) {
    if (!inst) return;
    inst->state = INTERLOCK_STATE_SAFE_IDLE;
    inst->auth_token = SAFETY_TOKEN_DISARMED;
    inst->timer_ms = 0;
    inst->hold_accum_ms = 0;
    inst->is_button_pressed = false;
    if (inst->config.on_state_change) {
        inst->config.on_state_change(INTERLOCK_STATE_ABORTED);
    }
}

void SafetyInterlock_SetButtonState(SafetyInterlock_t *inst, bool pressed) {
    if (!inst) return;
    inst->is_button_pressed = pressed;
}

// Викликається з фіксованим періодом dt_ms (наприклад, кожні 10 мс)
void SafetyInterlock_Tick(SafetyInterlock_t *inst, uint32_t dt_ms) {
    if (!inst) return;

    switch (inst->state) {
    case INTERLOCK_STATE_SAFE_IDLE:
        inst->auth_token = SAFETY_TOKEN_DISARMED;
        inst->hold_accum_ms = 0;
        break;

    case INTERLOCK_STATE_ARMED_LATCH:
        if (inst->auth_token != SAFETY_TOKEN_ARMED) {
            SafetyInterlock_Abort(inst);
            return;
        }

        if (inst->is_button_pressed) {
            inst->state = INTERLOCK_STATE_HOLD_PROGRESS;
            inst->hold_accum_ms = 0;
            if (inst->config.on_state_change) {
                inst->config.on_state_change(inst->state);
            }
        } else {
            if (inst->timer_ms <= dt_ms) {
                // Таймаут зведення вичерпано -> повернення в Safe
                SafetyInterlock_Abort(inst);
            } else {
                inst->timer_ms -= dt_ms;
            }
        }
        break;

    case INTERLOCK_STATE_HOLD_PROGRESS:
        if (inst->auth_token != SAFETY_TOKEN_ARMED) {
            SafetyInterlock_Abort(inst);
            return;
        }

        if (!inst->is_button_pressed) {
            // Зрив пальця / передчасне відпускання кнопки -> миттєвий скид
            SafetyInterlock_Abort(inst);
            return;
        }

        inst->hold_accum_ms += dt_ms;
        if (inst->hold_accum_ms >= inst->config.hold_required_ms) {
            if (inst->config.grace_countdown_ms > 0) {
                inst->state = INTERLOCK_STATE_COUNTDOWN_GRACE;
                inst->timer_ms = inst->config.grace_countdown_ms;
                if (inst->config.on_state_change) {
                    inst->config.on_state_change(inst->state);
                }
            } else {
                // Пряме спрацювання без вікна відліку
                inst->state = INTERLOCK_STATE_TRIGGERED;
                inst->auth_token = SAFETY_TOKEN_EXECUTE;
                if (inst->config.on_action_execute) {
                    inst->config.on_action_execute();
                }
                SafetyInterlock_Abort(inst);
            }
        }
        break;

    case INTERLOCK_STATE_COUNTDOWN_GRACE:
        if (inst->timer_ms <= dt_ms) {
            // Вікно відліку завершилося без скасування -> виконання дії
            inst->state = INTERLOCK_STATE_TRIGGERED;
            inst->auth_token = SAFETY_TOKEN_EXECUTE;
            if (inst->config.on_state_change) {
                inst->config.on_state_change(inst->state);
            }
            if (inst->config.on_action_execute) {
                inst->config.on_action_execute();
            }
            // Автоповернення в безпечний режим після завершення імпульсу
            SafetyInterlock_Abort(inst);
        } else {
            inst->timer_ms -= dt_ms;
        }
        break;

    default:
        SafetyInterlock_Abort(inst);
        break;
    }
}

// Отримання прогресу утримання у відсотках (0..100) для малювання UI
uint8_t SafetyInterlock_GetHoldProgressPct(const SafetyInterlock_t *inst) {
    if (!inst || inst->config.hold_required_ms == 0) return 0;
    if (inst->state != INTERLOCK_STATE_HOLD_PROGRESS) return 0;
    uint32_t pct = (inst->hold_accum_ms * 100U) / inst->config.hold_required_ms;
    return (pct > 100U) ? 100U : (uint8_t)pct;
}
