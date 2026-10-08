typedef struct {
    mcpwm_unit_t unit;
    mcpwm_timer_t timer;
    uint16_t calibrated_neutral_us;
    uint16_t deadband_us;
} calibrated_servo_t;

void calibrated_servo_write_pulse(calibrated_servo_t *servo, uint16_t target_us) {
    int32_t diff = (int32_t)target_us - servo->calibrated_neutral_us;
    uint16_t final_us;

    if (abs(diff) <= servo->deadband_us) {
        final_us = servo->calibrated_neutral_us;
    } else {
        final_us = target_us;
    }

    mcpwm_set_us(servo->unit, servo->timer, MCPWM_OPR_A, final_us);
}
