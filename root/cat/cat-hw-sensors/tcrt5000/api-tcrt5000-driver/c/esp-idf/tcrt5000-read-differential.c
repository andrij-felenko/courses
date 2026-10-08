tcrt5000_err_t tcrt5000_read_differential(tcrt5000_t *dev, uint16_t *diff_out) {
    if (!dev || !dev->initialized || dev->config.gpio_emitter_ctrl < 0) {
        return TCRT5000_ERR_INVALID_ARG;
    }

    uint16_t v_off = 0;
    uint16_t v_on = 0;

    // 1. Зчитування фонового рівня (LED OFF)
    tcrt5000_read_analog_raw(dev, &v_off);

    // Перевірка насичення фототранзистора зовнішнім світлом
    if (v_off > 3900) {
        return TCRT5000_ERR_SATURATION;
    }

    // 2. Зчитування рівня при спалаху (LED ON)
    tcrt5000_read_analog_raw(dev, &v_on);

    // Перевірка апаратного обриву
    if (v_on < 10 && v_off < 10) {
        return TCRT5000_ERR_DISCONNECTED;
    }

    // Обчислення диференційного значення
    if (v_on >= v_off) {
        *diff_out = v_on - v_off;
    } else {
        *diff_out = 0;
    }

    return TCRT5000_OK;
}
