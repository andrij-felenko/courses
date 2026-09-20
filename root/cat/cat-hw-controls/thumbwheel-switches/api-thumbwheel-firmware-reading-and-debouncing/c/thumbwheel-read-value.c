bool thumbwheel_read_value(thumbwheel_driver_t *driver, uint32_t *out_value) {
    if (!driver || !out_value || !driver->config) return false;
    const thumbwheel_config_t *cfg = driver->config;

    uint32_t total = 0;
    uint32_t multiplier = 1;

    for (uint8_t i = 0; i < cfg->num_decades; i++) {
        const thumbwheel_decade_state_t *st = &driver->decades[i];

        if (!st->is_valid || st->debounced_code > 9) {
            driver->has_error = true;
            return false;
        }

        total += (uint32_t)st->debounced_code * multiplier;
        multiplier *= 10;
    }

    driver->validated_value = total;
    driver->has_error = false;
    *out_value = total;
    return true;
}
