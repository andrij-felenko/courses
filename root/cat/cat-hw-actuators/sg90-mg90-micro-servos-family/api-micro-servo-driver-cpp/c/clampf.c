static float clampf(float v, float min, float max) {
    return (v < min) ? min : ((v > max) ? max : v);
}

servo_status_t servo_set_angle(servo_t *servo, float angle_deg) {
    if (!servo || !servo->is_attached) return SERVO_ERR_INVALID_PARAM;
    float clamped_angle = clampf(angle_deg, servo->cfg.soft_limit_min_deg, servo->cfg.soft_limit_max_deg);
    float span_angle = servo->cfg.max_angle_deg - servo->cfg.min_angle_deg;
    float span_pulse = (float)(servo->cfg.max_pulse_us - servo->cfg.min_pulse_us);

    float pulse = (float)servo->cfg.min_pulse_us +
                  (clamped_angle - servo->cfg.min_angle_deg) * span_pulse / span_angle;

    servo->current_angle = clamped_angle;
    servo->cfg.set_pwm_us((uint16_t)(pulse + 0.5f));
    return SERVO_OK;
}

servo_status_t servo_set_pulse_us(servo_t *servo, uint16_t pulse_us) {
    if (!servo || !servo->is_attached) return SERVO_ERR_INVALID_PARAM;
    if (pulse_us < servo->cfg.min_pulse_us) pulse_us = servo->cfg.min_pulse_us;
    if (pulse_us > servo->cfg.max_pulse_us) pulse_us = servo->cfg.max_pulse_us;

    servo->cfg.set_pwm_us(pulse_us);
    return SERVO_OK;
}
