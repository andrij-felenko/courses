void thumbwheel_scan_tick(thumbwheel_driver_t *driver) {
    if (!driver || !driver->config) return;
    const thumbwheel_config_t *cfg = driver->config;

    for (uint8_t i = 0; i < cfg->num_decades; i++) {
        uint8_t raw = 0;
        if (cfg->active_low) {
            raw = (~raw) & 0x0F;
        } else {
            raw = raw & 0x0F;
        }

        thumbwheel_decade_state_t *st = &driver->decades[i];
        st->raw_code = raw;

        bool valid = true;
        if (cfg->code_type == THUMBWHEEL_CODE_BCD_DIRECT || 
            cfg->code_type == THUMBWHEEL_CODE_BCD_COMPLEMENT) {
            if (raw > 9) {
                valid = false;
            }
        }

        st->is_valid = valid;

        if (valid && (raw == st->candidate_code)) {
            if (st->stability_counter < cfg->debounce_ticks) {
                st->stability_counter++;
                if (st->stability_counter >= cfg->debounce_ticks) {
                    st->debounced_code = raw;
                }
            }
        } else {
            st->candidate_code = valid ? raw : 0xFF;
            st->stability_counter = 0;
        }
    }
}
