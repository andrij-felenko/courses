#include <stdint.h>
#include <stdbool.h>

/* Стан автомата софтстартера */
typedef enum {
    SS_STATE_IDLE,
    SS_STATE_KICKSTART,
    SS_STATE_RAMP_UP,
    SS_STATE_FULL_ON,
    SS_STATE_BYPASS,
    SS_STATE_RAMP_DOWN,
    SS_STATE_FAULT
} SoftStartState;

/* Коди помилок захисту приводу */
typedef enum {
    SS_FAULT_NONE = 0,
    SS_FAULT_PHASE_LOSS,
    SS_FAULT_OVERCURRENT,
    SS_FAULT_STALL,
    SS_FAULT_OVERHEAT
} SoftStartFault;

/* Параметри конфігурації приводу */
typedef struct {
    uint32_t kickstart_time_ms;   /* Час імпульсу поштовху, мс (0 = вимкнено) */
    uint16_t kickstart_alpha_deg;  /* Кут для поштовху (типово 45..60 град) */
    uint32_t ramp_up_time_ms;     /* Час розгону напруги, мс */
    uint32_t ramp_down_time_ms;   /* Час плавної зупинки, мс */
    uint16_t initial_alpha_deg;   /* Початковий кут пуску (типово 135 град) */
    uint16_t stop_alpha_deg;      /* Кінцевий кут зупинки (типово 145 град) */
    float    i_limit_amps;        /* Максимально допустимий пусковий струм */
    float    kp;                  /* Пропорційний коефіцієнт струмового ПІД */
    float    ki;                  /* Інтегральний коефіцієнт струмового ПІД */
} SoftStartConfig;

/* Робочий контекст контролера */
typedef struct {
    SoftStartState  state;
    SoftStartFault  fault;
    SoftStartConfig cfg;
    float           current_alpha_deg;
    uint32_t        state_timer_ms;
    float           i_integral_err;
    bool            bypass_relay_cmd;
    bool            gate_pulses_enabled;
} SoftStartController;

/* Ініціалізація структури контролера */
void softstart_init(SoftStartController *ctrl, const SoftStartConfig *cfg) {
    ctrl->cfg = *cfg;
    ctrl->state = SS_STATE_IDLE;
    ctrl->fault = SS_FAULT_NONE;
    ctrl->current_alpha_deg = cfg->initial_alpha_deg;
    ctrl->state_timer_ms = 0;
    ctrl->i_integral_err = 0.0f;
    ctrl->bypass_relay_cmd = false;
    ctrl->gate_pulses_enabled = false;
}

/* Команда запуску двигуна */
void softstart_start_command(SoftStartController *ctrl) {
    if (ctrl->state != SS_STATE_IDLE) return;

    ctrl->state_timer_ms = 0;
    ctrl->i_integral_err = 0.0f;
    ctrl->gate_pulses_enabled = true;
    ctrl->bypass_relay_cmd = false;
    ctrl->fault = SS_FAULT_NONE;

    if (ctrl->cfg.kickstart_time_ms > 0) {
        ctrl->state = SS_STATE_KICKSTART;
        ctrl->current_alpha_deg = (float)ctrl->cfg.kickstart_alpha_deg;
    } else {
        ctrl->state = SS_STATE_RAMP_UP;
        ctrl->current_alpha_deg = (float)ctrl->cfg.initial_alpha_deg;
    }
}

/* Команда плавної зупинки */
void softstart_stop_command(SoftStartController *ctrl) {
    if (ctrl->state == SS_STATE_BYPASS || ctrl->state == SS_STATE_FULL_ON) {
        ctrl->state = SS_STATE_RAMP_DOWN;
        ctrl->state_timer_ms = 0;
        ctrl->gate_pulses_enabled = true;  /* Тиристори підхоплюють струм */
        ctrl->bypass_relay_cmd = false;    /* Контактор розмикається */
        ctrl->current_alpha_deg = 0.0f;
    }
}

/* Основний такт FSM (викликається кожні 10 мс на кожному напівперіоді мережі) */
void softstart_process_half_cycle(SoftStartController *ctrl, float measured_current_rms, uint32_t dt_ms) {
    ctrl->state_timer_ms += dt_ms;

    switch (ctrl->state) {
        case SS_STATE_IDLE:
            ctrl->gate_pulses_enabled = false;
            ctrl->bypass_relay_cmd = false;
            break;

        case SS_STATE_KICKSTART:
            if (ctrl->state_timer_ms >= ctrl->cfg.kickstart_time_ms) {
                ctrl->state = SS_STATE_RAMP_UP;
                ctrl->state_timer_ms = 0;
                ctrl->current_alpha_deg = (float)ctrl->cfg.initial_alpha_deg;
            }
            break;

        case SS_STATE_RAMP_UP: {
            /* Базовий крок зменшення кута альфа за час розгону */
            float ramp_progress = (float)ctrl->state_timer_ms / (float)ctrl->cfg.ramp_up_time_ms;
            if (ramp_progress > 1.0f) ramp_progress = 1.0f;

            float target_alpha = (float)ctrl->cfg.initial_alpha_deg * (1.0f - ramp_progress);

            /* Замкнений контур обмеження струму (Current Limit PI) */
            if (measured_current_rms > ctrl->cfg.i_limit_amps) {
                float err = measured_current_rms - ctrl->cfg.i_limit_amps;
                ctrl->i_integral_err += err * ((float)dt_ms / 1000.0f);
                float pi_correction = (ctrl->cfg.kp * err) + (ctrl->cfg.ki * ctrl->i_integral_err);
                target_alpha += pi_correction; /* Збільшуємо кут для зниження струму */
                if (target_alpha > (float)ctrl->cfg.initial_alpha_deg) {
                    target_alpha = (float)ctrl->cfg.initial_alpha_deg;
                }
            } else {
                if (ctrl->i_integral_err > 0.0f) {
                    ctrl->i_integral_err -= 0.1f * ((float)dt_ms / 1000.0f);
                    if (ctrl->i_integral_err < 0.0f) ctrl->i_integral_err = 0.0f;
                }
            }

            ctrl->current_alpha_deg = target_alpha;

            if (ramp_progress >= 1.0f && ctrl->current_alpha_deg <= 2.0f) {
                ctrl->current_alpha_deg = 0.0f;
                ctrl->state = SS_STATE_FULL_ON;
                ctrl->state_timer_ms = 0;
            }
            break;
        }

        case SS_STATE_FULL_ON:
            /* Повна провідність: вмикаємо байпасний контактор */
            ctrl->current_alpha_deg = 0.0f;
            ctrl->bypass_relay_cmd = true;
            /* Чекаємо 100 мс на фізичне замикання контактів KM1 */
            if (ctrl->state_timer_ms >= 100) {
                ctrl->state = SS_STATE_BYPASS;
                ctrl->gate_pulses_enabled = false; /* Знімаємо імпульси з тиристорів */
            }
            break;

        case SS_STATE_BYPASS:
            ctrl->gate_pulses_enabled = false;
            ctrl->bypass_relay_cmd = true;
            break;

        case SS_STATE_RAMP_DOWN: {
            float stop_progress = (float)ctrl->state_timer_ms / (float)ctrl->cfg.ramp_down_time_ms;
            if (stop_progress > 1.0f) stop_progress = 1.0f;

            ctrl->current_alpha_deg = (float)ctrl->cfg.stop_alpha_deg * stop_progress;

            if (stop_progress >= 1.0f) {
                ctrl->state = SS_STATE_IDLE;
                ctrl->gate_pulses_enabled = false;
                ctrl->bypass_relay_cmd = false;
            }
            break;
        }

        case SS_STATE_FAULT:
            ctrl->gate_pulses_enabled = false;
            ctrl->bypass_relay_cmd = false;
            break;
    }
}

/* Розрахунок затримки таймера для переривання запуску тиристора (для 50 Гц: півперіод = 10000 мкс) */
uint32_t softstart_calculate_timer_delay_us(float alpha_deg) {
    if (alpha_deg <= 0.0f) return 0;
    if (alpha_deg >= 180.0f) return 10000;
    return (uint32_t)((alpha_deg / 180.0f) * 10000.0f);
}
