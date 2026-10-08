#include <stdint.h>
#include <stdbool.h>

typedef enum {
    PUMP_STATE_IDLE = 0,
    PUMP_STATE_RUNNING,
    PUMP_STATE_VERIFYING,
    PUMP_STATE_RETRY_PULSE,
    PUMP_STATE_THERMAL_COOLING,
    PUMP_STATE_FAULT_LOCKOUT
} pump_state_t;

typedef struct {
    uint32_t current_low_threshold_ma;
    uint32_t current_high_threshold_ma;
    uint32_t debounce_ms;
    uint32_t pulse_on_ms;
    uint32_t pulse_off_ms;
    uint32_t cooling_ms;
    uint8_t  max_retries;
} pump_config_t;

typedef struct {
    pump_state_t state;
    uint8_t  retry_count;
    uint32_t state_timer_ms;
    uint32_t pulse_timer_ms;
    bool     output_active;
} pump_controller_t;

static pump_controller_t g_pump;
static const pump_config_t g_cfg = {
    .current_low_threshold_ma = 40,
    .current_high_threshold_ma = 350,
    .debounce_ms = 150,
    .pulse_on_ms = 100,
    .pulse_off_ms = 900,
    .cooling_ms = 5000,
    .max_retries = 3
};

// Заглушки апаратного рівня (виклики периферії)
static inline uint32_t hw_read_current_ma(void) { return 30; } // Симуляція провалу струму
static inline uint32_t hw_get_time_ms(void) { return 0; }     // Повертає системний час у мс
static inline void hw_set_pump_power(bool enable) { (void)enable; }

void pump_fsm_init(void) {
    g_pump.state = PUMP_STATE_IDLE;
    g_pump.retry_count = 0;
    g_pump.state_timer_ms = 0;
    g_pump.pulse_timer_ms = 0;
    g_pump.output_active = false;
    hw_set_pump_power(false);
}

void pump_fsm_start(void) {
    if (g_pump.state == PUMP_STATE_IDLE) {
        g_pump.state = PUMP_STATE_RUNNING;
        g_pump.retry_count = 0;
        g_pump.output_active = true;
        hw_set_pump_power(true);
    }
}

void pump_fsm_process(uint32_t now_ms) {
    uint32_t current_ma = hw_read_current_ma();

    switch (g_pump.state) {
        case PUMP_STATE_IDLE:
            break;

        case PUMP_STATE_RUNNING:
            if (current_ma < g_cfg.current_low_threshold_ma || current_ma > g_cfg.current_high_threshold_ma) {
                g_pump.state = PUMP_STATE_VERIFYING;
                g_pump.state_timer_ms = now_ms;
            }
            break;

        case PUMP_STATE_VERIFYING:
            if (current_ma >= g_cfg.current_low_threshold_ma && current_ma <= g_cfg.current_high_threshold_ma) {
                g_pump.state = PUMP_STATE_RUNNING;
            } else if (now_ms - g_pump.state_timer_ms >= g_cfg.debounce_ms) {
                g_pump.state = PUMP_STATE_RETRY_PULSE;
                g_pump.pulse_timer_ms = now_ms;
                g_pump.output_active = true;
                hw_set_pump_power(true);
            }
            break;

        case PUMP_STATE_RETRY_PULSE:
            if (current_ma >= g_cfg.current_low_threshold_ma && current_ma <= g_cfg.current_high_threshold_ma) {
                g_pump.state = PUMP_STATE_RUNNING;
                g_pump.retry_count = 0;
                break;
            }

            if (g_pump.output_active) {
                if (now_ms - g_pump.pulse_timer_ms >= g_cfg.pulse_on_ms) {
                    g_pump.output_active = false;
                    hw_set_pump_power(false);
                    g_pump.pulse_timer_ms = now_ms;
                    g_pump.retry_count++;
                }
            } else {
                if (now_ms - g_pump.pulse_timer_ms >= g_cfg.pulse_off_ms) {
                    if (g_pump.retry_count >= g_cfg.max_retries) {
                        g_pump.state = PUMP_STATE_THERMAL_COOLING;
                        g_pump.state_timer_ms = now_ms;
                    } else {
                        g_pump.output_active = true;
                        hw_set_pump_power(true);
                        g_pump.pulse_timer_ms = now_ms;
                    }
                }
            }
            break;

        case PUMP_STATE_THERMAL_COOLING:
            hw_set_pump_power(false);
            if (now_ms - g_pump.state_timer_ms >= g_cfg.cooling_ms) {
                g_pump.state = PUMP_STATE_FAULT_LOCKOUT;
            }
            break;

        case PUMP_STATE_FAULT_LOCKOUT:
            hw_set_pump_power(false);
            break;
    }
}
