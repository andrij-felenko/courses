typedef struct {
    mcpwm_unit_t unit;
    mcpwm_timer_t timer;
    int gpio_pin;
    TickType_t last_cmd_tick;
    TickType_t timeout_ticks;
    bool active;
} safe_servo_t;

void safe_servo_update_cmd(safe_servo_t *servo, uint16_t pulse_us) {
    if (!servo->active) {
        mcpwm_start(servo->unit, servo->timer);
        servo->active = true;
    }
    mcpwm_set_us(servo->unit, servo->timer, MCPWM_OPR_A, pulse_us);
    servo->last_cmd_tick = xTaskGetTickCount();
}

void safe_servo_watchdog_check(safe_servo_t *servo) {
    if (servo->active && (xTaskGetTickCount() - servo->last_cmd_tick > servo->timeout_ticks)) {
        mcpwm_stop(servo->unit, servo->timer); // Аварійна зупинка ШІМ-сигналу
        servo->active = false;
    }
}
