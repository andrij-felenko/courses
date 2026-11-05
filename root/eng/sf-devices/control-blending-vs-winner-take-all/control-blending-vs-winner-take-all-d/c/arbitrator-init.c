#include <stdint.h>
#include <stdbool.h>
#include <math.h>

typedef enum {
    ARBITER_MODE_BLENDING = 0,
    ARBITER_MODE_RAMPING,
    ARBITER_MODE_WINNER_TAKE_ALL
} arbiter_mode_t;

typedef struct {
    float command;         // Значення сигналу [-1.0f, +1.0f]
    uint32_t timestamp_ms; // Часовий штамп отримання
    bool valid;            // Прапорець свіжості та валідності
} control_command_t;

typedef struct {
    float min_output;      // Фізична нижня межа актуатора
    float max_output;      // Фізична верхня межа актуатора
    float max_slew_rate;   // Максимальна швидкість зміни (од/сек)
    float s_low;           // Межа 100% автопілота
    float s_high;          // Межа 100% ручного керування
    float s_emergency;     // Поріг аварійного витіснення
    float s_hysteresis;    // Вікно гістерезису для виходу з аварії
    uint32_t timeout_ms;   // Таймаут застарілості даних (мс)
} arbiter_config_t;

typedef struct {
    arbiter_config_t config;
    arbiter_mode_t current_mode;
    float prev_output;
} control_arbitrator_t;

void arbitrator_init(control_arbitrator_t *arb, const arbiter_config_t *cfg) {
    if (arb && cfg) {
        arb->config = *cfg;
        arb->current_mode = ARBITER_MODE_BLENDING;
        arb->prev_output = 0.0f;
    }
}

float arbitrator_process(control_arbitrator_t *arb,
                         const control_command_t *human,
                         const control_command_t *auto_ctrl,
                         const control_command_t *safety,
                         float safety_distance,
                         uint32_t current_time_ms,
                         float dt_sec) {
    if (!arb) return 0.0f;

    const arbiter_config_t *cfg = &arb->config;

    // 1. Валідація застарілості джерел керування
    bool human_valid = human && human->valid && 
                       ((current_time_ms - human->timestamp_ms) <= cfg->timeout_ms);
    bool auto_valid  = auto_ctrl && auto_ctrl->valid && 
                       ((current_time_ms - auto_ctrl->timestamp_ms) <= cfg->timeout_ms);
    bool safety_valid = safety && safety->valid && 
                        ((current_time_ms - safety->timestamp_ms) <= cfg->timeout_ms);

    // 2. Гістерезисний селектор режиму арбітражу
    if (arb->current_mode == ARBITER_MODE_WINNER_TAKE_ALL) {
        if (safety_distance > (cfg->s_emergency + cfg->s_hysteresis)) {
            arb->current_mode = ARBITER_MODE_RAMPING;
        }
    } else {
        if (safety_valid && (safety_distance < cfg->s_emergency)) {
            arb->current_mode = ARBITER_MODE_WINNER_TAKE_ALL;
        }
    }

    float raw_target = 0.0f;

    // 3. Формування базового цільового сигналу
    if (arb->current_mode == ARBITER_MODE_WINNER_TAKE_ALL) {
        raw_target = safety_valid ? safety->command : 0.0f;
    } else {
        if (human_valid && auto_valid) {
            // Опукле злиття (Convex Blending)
            float w_auto = 0.0f;
            if (safety_distance <= cfg->s_low) {
                w_auto = 1.0f;
            } else if (safety_distance >= cfg->s_high) {
                w_auto = 0.0f;
            } else {
                float ds = cfg->s_high - cfg->s_low;
                float norm_s = (cfg->s_high - safety_distance) / ds;
                w_auto = norm_s * norm_s * (3.0f - 2.0f * norm_s); // Кубічний сплайн
            }
            float w_human = 1.0f - w_auto;
            raw_target = w_human * human->command + w_auto * auto_ctrl->command;
        } else if (human_valid) {
            raw_target = human->command;
        } else if (auto_valid) {
            raw_target = auto_ctrl->command;
        } else if (safety_valid) {
            raw_target = safety->command;
        } else {
            raw_target = 0.0f; // Режим за замовчуванням при втраті всіх сигналів
        }
    }

    // 4. Slew Rate Limiter (Обмеження швидкості зміни)
    float max_delta = cfg->max_slew_rate * dt_sec;
    float delta = raw_target - arb->prev_output;
    if (delta > max_delta) {
        delta = max_delta;
    } else if (delta < -max_delta) {
        delta = -max_delta;
    }
    float ramped_output = arb->prev_output + delta;

    // 5. Проекція на фізичні межі безпеки
    if (ramped_output > cfg->max_output) {
        ramped_output = cfg->max_output;
    } else if (ramped_output < cfg->min_output) {
        ramped_output = cfg->min_output;
    }

    arb->prev_output = ramped_output;
    return ramped_output;
}
