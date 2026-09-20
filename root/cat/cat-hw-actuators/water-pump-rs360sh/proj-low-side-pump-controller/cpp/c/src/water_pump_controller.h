#ifndef WATER_PUMP_CONTROLLER_H
#define WATER_PUMP_CONTROLLER_H

#include <stdint.h>
#include <stdbool.h>

// Функція зворотного виклику для встановлення ШІМ
typedef void (*pwm_set_duty_cb_t)(uint8_t duty);

// Функція для отримання поточного часу в мілісекундах
typedef uint32_t (*get_time_ms_cb_t)(void);

typedef struct {
    uint32_t soft_start_duration_ms;
    uint32_t watchdog_timeout_ms;
    uint8_t min_duty_cycle;
    uint8_t max_duty_cycle;
    pwm_set_duty_cb_t pwm_set_duty;
    get_time_ms_cb_t get_time_ms;
} water_pump_config_t;

typedef enum {
    PUMP_STATE_STOPPED,
    PUMP_STATE_STARTING,
    PUMP_STATE_RUNNING,
    PUMP_STATE_FAULT
} water_pump_state_t;

typedef struct {
    water_pump_config_t config;
    water_pump_state_t state;
    uint32_t state_start_time;
    uint32_t last_watchdog_reset;
} water_pump_controller_t;

void water_pump_init(water_pump_controller_t* p_ctrl, const water_pump_config_t* p_config);
void water_pump_start(water_pump_controller_t* p_ctrl);
void water_pump_stop(water_pump_controller_t* p_ctrl);
void water_pump_update(water_pump_controller_t* p_ctrl);
void water_pump_reset_watchdog(water_pump_controller_t* p_ctrl);
bool water_pump_is_fault(const water_pump_controller_t* p_ctrl);

#endif // WATER_PUMP_CONTROLLER_H
