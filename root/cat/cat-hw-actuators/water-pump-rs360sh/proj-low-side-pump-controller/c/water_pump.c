#include "water_pump.h"

void WaterPump_Init(WaterPump_t *pump, 
                    WaterPumpConfig_t *config, 
                    void (*set_pwm)(uint8_t), 
                    uint32_t (*get_time_ms)(void)) {
    if (!pump) return;
    
    pump->state = PUMP_STATE_IDLE;
    if (config) {
        pump->config = *config;
    } else {
        /* Значення за замовчуванням */
        pump->config.soft_start_duration_ms = 1000;
        pump->config.max_run_time_ms = 60000;
        pump->config.target_duty_cycle = 100;
    }
    
    pump->set_pwm_cb = set_pwm;
    pump->get_time_ms_cb = get_time_ms;
    pump->current_duty = 0;
    
    if (pump->set_pwm_cb) {
        pump->set_pwm_cb(0);
    }
}

void WaterPump_Start(WaterPump_t *pump) {
    if (!pump || pump->state != PUMP_STATE_IDLE || !pump->get_time_ms_cb) return;
    
    uint32_t current_time = pump->get_time_ms_cb();
    
    pump->state = PUMP_STATE_STARTING;
    pump->soft_start_start_ms = current_time;
    pump->start_time_ms = current_time;
    pump->current_duty = 0;
}

void WaterPump_Stop(WaterPump_t *pump) {
    if (!pump) return;
    
    pump->state = PUMP_STATE_IDLE;
    pump->current_duty = 0;
    
    if (pump->set_pwm_cb) {
        pump->set_pwm_cb(0);
    }
}

void WaterPump_Update(WaterPump_t *pump) {
    if (!pump || !pump->get_time_ms_cb || !pump->set_pwm_cb) return;
    
    if (pump->state == PUMP_STATE_IDLE) {
        return;
    }
    
    uint32_t current_time = pump->get_time_ms_cb();
    
    /* Перевірка захисного таймера: вимикаємо, якщо працює занадто довго */
    if (current_time - pump->start_time_ms >= pump->config.max_run_time_ms) {
        WaterPump_Stop(pump);
        return;
    }
    
    /* Логіка плавного пуску (кінцевий автомат) */
    if (pump->state == PUMP_STATE_STARTING) {
        uint32_t elapsed = current_time - pump->soft_start_start_ms;
        
        if (elapsed >= pump->config.soft_start_duration_ms) {
            pump->current_duty = pump->config.target_duty_cycle;
            pump->state = PUMP_STATE_RUNNING;
        } else {
            /* Пропорційне збільшення ШІМ */
            pump->current_duty = (uint8_t)((elapsed * pump->config.target_duty_cycle) / 
                                            pump->config.soft_start_duration_ms);
        }
        pump->set_pwm_cb(pump->current_duty);
    }
    else if (pump->state == PUMP_STATE_RUNNING) {
        /* ШІМ вже встановлено, очікуємо зупинки або спрацьовування захисту */
    }
}
