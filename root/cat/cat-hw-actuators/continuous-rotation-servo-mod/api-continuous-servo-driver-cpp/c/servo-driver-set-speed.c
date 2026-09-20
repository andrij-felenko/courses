typedef struct {
    servo_continuous_config_t cfg;
    float current_speed;
    float target_speed;
    float max_accel;
    uint32_t timeout_ms;
    uint32_t last_cmd_ms;
} servo_driver_t;

void servo_driver_set_speed(servo_driver_t *d, float speed, uint32_t now_ms) {
    d->target_speed = (speed > 1.0f) ? 1.0f : ((speed < -1.0f) ? -1.0f : speed);
    d->last_cmd_ms = now_ms;
}

void servo_driver_update(servo_driver_t *d, uint32_t now_ms, uint32_t dt_ms) {
    if (now_ms - d->last_cmd_ms > d->timeout_ms) {
        d->target_speed = 0.0f;
    }
    float step = d->max_accel * (dt_ms / 1000.0f);
    float diff = d->target_speed - d->current_speed;
    if (diff > step) d->current_speed += step;
    else if (diff < -step) d->current_speed -= step;
    else d->current_speed = d->target_speed;
    servo_continuous_set_speed(&d->cfg, d->current_speed);
}
