#include "water_pump_controller.h"

void water_pump_init(water_pump_controller_t* p_ctrl, const water_pump_config_t* p_config) {
    p_ctrl->config = *p_config;
    p_ctrl->state = PUMP_STATE_STOPPED;
    p_ctrl->state_start_time = 0;
    p_ctrl->last_watchdog_reset = 0;
    
    if (p_ctrl->config.pwm_set_duty) {
        p_ctrl->config.pwm_set_duty(0);
    }
}

void water_pump_start(water_pump_controller_t* p_ctrl) {
    if (p_ctrl->state == PUMP_STATE_STOPPED || p_ctrl->state == PUMP_STATE_FAULT) {
        p_ctrl->state = PUMP_STATE_STARTING;
        p_ctrl->state_start_time = p_ctrl->config.get_time_ms();
        p_ctrl->last_watchdog_reset = p_ctrl->state_start_time;
        
        if (p_ctrl->config.pwm_set_duty) {
            p_ctrl->config.pwm_set_duty(p_ctrl->config.min_duty_cycle);
        }
    }
}

void water_pump_stop(water_pump_controller_t* p_ctrl) {
    p_ctrl->state = PUMP_STATE_STOPPED;
    if (p_ctrl->config.pwm_set_duty) {
        p_ctrl->config.pwm_set_duty(0);
    }
}

void water_pump_reset_watchdog(water_pump_controller_t* p_ctrl) {
    p_ctrl->last_watchdog_reset = p_ctrl->config.get_time_ms();
}

bool water_pump_is_fault(const water_pump_controller_t* p_ctrl) {
    return p_ctrl->state == PUMP_STATE_FAULT;
}

void water_pump_update(water_pump_controller_t* p_ctrl) {
    if (p_ctrl->state == PUMP_STATE_STOPPED || p_ctrl->state == PUMP_STATE_FAULT) {
        return;
    }

    uint32_t now = p_ctrl->config.get_time_ms();

    // Перевірка сторожового таймера
    if ((now - p_ctrl->last_watchdog_reset) >= p_ctrl->config.watchdog_timeout_ms) {
        p_ctrl->state = PUMP_STATE_FAULT;
        if (p_ctrl->config.pwm_set_duty) {
            p_ctrl->config.pwm_set_duty(0);
        }
        return;
    }

    // Плавний пуск
    if (p_ctrl->state == PUMP_STATE_STARTING) {
        uint32_t elapsed = now - p_ctrl->state_start_time;
        if (elapsed >= p_ctrl->config.soft_start_duration_ms) {
            p_ctrl->state = PUMP_STATE_RUNNING;
            if (p_ctrl->config.pwm_set_duty) {
                p_ctrl->config.pwm_set_duty(p_ctrl->config.max_duty_cycle);
            }
        } else {
            // Лінійна інтерполяція ШІМ
            float progress = (float)elapsed / p_ctrl->config.soft_start_duration_ms;
            uint8_t duty = p_ctrl->config.min_duty_cycle + 
                (uint8_t)(progress * (p_ctrl->config.max_duty_cycle - p_ctrl->config.min_duty_cycle));
            if (p_ctrl->config.pwm_set_duty) {
                p_ctrl->config.pwm_set_duty(duty);
            }
        }
    }
}
