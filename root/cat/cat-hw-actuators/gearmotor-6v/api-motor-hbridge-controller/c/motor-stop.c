motor_status_t motor_stop(motor_t *motor, motor_stop_mode_t mode)
{
    if (motor == NULL) {
        return MOTOR_ERR_NULL_PTR;
    }
    if (motor->state == MOTOR_STATE_UNINITIALIZED) {
        return MOTOR_ERR_INVALID_PARAM;
    }

    // Негайне скидання каналів ШІМ до нульового коефіцієнта заповнення
    platform_pwm_set_duty(motor->config.port_in1, motor->config.pin_in1, 0);
    platform_pwm_set_duty(motor->config.port_in2, motor->config.pin_in2, 0);

    if (mode == MOTOR_STOP_BRAKE) {
        // Динамічне гальмування (BRAKE): обидва виводи замикаються на землю (LOW)
        // або переводяться у стан HIGH залежно від логіки конкретної мікросхеми моста
        // Для драйверів типу DRV8833/TB6612 подача HIGH на обидва входи відкриває нижні ключі
        platform_gpio_write(motor->config.port_in1, motor->config.pin_in1, true);
        platform_gpio_write(motor->config.port_in2, motor->config.pin_in2, true);
    } else {
        // Вільний вибіг (COAST): усі ключі моста розімкнені (стан Hi-Z)
        // Подача LOW на обидва входи повністю закриває всі чотири силові транзистори
        platform_gpio_write(motor->config.port_in1, motor->config.pin_in1, false);
        platform_gpio_write(motor->config.port_in2, motor->config.pin_in2, false);
    }

    motor->current_speed = 0.0f;
    motor->current_duty = 0.0f;
    motor->state = MOTOR_STATE_IDLE;

    return MOTOR_OK;
}
