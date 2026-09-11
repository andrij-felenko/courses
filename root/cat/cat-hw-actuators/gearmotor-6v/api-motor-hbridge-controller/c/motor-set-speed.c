motor_status_t motor_set_speed(motor_t *motor, float speed)
{
    if (motor == NULL) {
        return MOTOR_ERR_NULL_PTR;
    }
    if (motor->state != MOTOR_STATE_IDLE && motor->state != MOTOR_STATE_RUNNING) {
        return MOTOR_ERR_INVALID_PARAM;
    }

    // Обмеження вхідного значення діапазоном [-1.0 .. +1.0]
    if (speed > 1.0f) {
        speed = 1.0f;
    } else if (speed < -1.0f) {
        speed = -1.0f;
    }

    float abs_speed = fabsf(speed);

    // Перевірка порогу відсікання шуму навколо нуля
    if (abs_speed < motor->config.deadband_cutoff) {
        motor_stop(motor, MOTOR_STOP_COAST);
        motor->current_speed = 0.0f;
        motor->current_duty = 0.0f;
        return MOTOR_OK;
    }

    // Лінійна компенсація мертвої зони (ремапінг)
    float scale = (1.0f - motor->config.deadband_min_duty) / (1.0f - motor->config.deadband_cutoff);
    float duty = motor->config.deadband_min_duty + (abs_speed - motor->config.deadband_cutoff) * scale;

    if (duty > 1.0f) {
        duty = 1.0f;
    }

    // Розрахунок порогу порівняння таймера у відліках
    uint32_t compare_value = (uint32_t)roundf(duty * (float)motor->timer_arr);

    // Комутація напівмостів відповідно до знака швидкості
    if (speed > 0.0f) {
        // Обертання вперед: IN1 генерує ШІМ, IN2 утримується на нулі
        platform_gpio_write(motor->config.port_in2, motor->config.pin_in2, false);
        platform_pwm_set_duty(motor->config.port_in1, motor->config.pin_in1, compare_value);
    } else {
        // Реверс: IN1 утримується на нулі, IN2 генерує ШІМ
        platform_gpio_write(motor->config.port_in1, motor->config.pin_in1, false);
        platform_pwm_set_duty(motor->config.port_in2, motor->config.pin_in2, compare_value);
    }

    motor->current_speed = speed;
    motor->current_duty = duty;
    motor->state = MOTOR_STATE_RUNNING;

    return MOTOR_OK;
}
