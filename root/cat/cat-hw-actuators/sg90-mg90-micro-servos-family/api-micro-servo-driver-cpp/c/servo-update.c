typedef struct {
    float max_speed_deg_s;  // Гранична швидкість (°/с)
    float target_angle;     // Цільовий кут (°)
} servo_motion_t;

void servo_update(servo_t *servo, servo_motion_t *motion, float dt_s) {
    if (!servo || !servo->is_attached || !motion) return;
    float diff = motion->target_angle - servo->current_angle;
    if (fabsf(diff) < 0.01f) return;

    float max_step = motion->max_speed_deg_s * dt_s;
    if (fabsf(diff) <= max_step) {
        servo_set_angle(servo, motion->target_angle);
    } else {
        float step = (diff > 0.0f) ? max_step : -max_step;
        servo_set_angle(servo, servo->current_angle + step);
    }
}
