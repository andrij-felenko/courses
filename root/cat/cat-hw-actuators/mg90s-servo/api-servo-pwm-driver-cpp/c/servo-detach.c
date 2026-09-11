/**
 * @brief Безпечне відключення генерації ШІМ (перехід у знеструмлений стан).
 * @param servo Покажчик на дескриптор привода.
 * @return Код результату servo_status_t.
 */
servo_status_t servo_detach(servo_t *servo) {
    if (servo == NULL) {
        return SERVO_ERR_INVALID_ARG;
    }
    if (!servo->is_attached) {
        return SERVO_OK; // Вже знеструмлений
    }

    // Виклик платформно-залежної функції вимкнення апаратного каналу таймера
    if (servo->hal_set_pwm_enabled != NULL) {
        servo->hal_set_pwm_enabled(servo->timer_instance, servo->channel, false);
    }

    servo->is_attached = false;
    return SERVO_OK;
}

/**
 * @brief Безпечне відновлення генерації ШІМ з фіксацією позиції.
 * @param servo Покажчик на дескриптор привода.
 * @return Код результату servo_status_t.
 */
servo_status_t servo_attach(servo_t *servo) {
    if (servo == NULL) {
        return SERVO_ERR_INVALID_ARG;
    }
    if (servo->is_attached) {
        return SERVO_OK; // Вже активний
    }

    // Спочатку записуємо безпечне значення імпульсу в регістр
    servo_write_angle(servo, servo->current_angle_deg);

    // Вмикаємо вихід апаратного таймера
    if (servo->hal_set_pwm_enabled != NULL) {
        servo->hal_set_pwm_enabled(servo->timer_instance, servo->channel, true);
    }

    servo->is_attached = true;
    return SERVO_OK;
}
