// Старт лише в межах ТЗ: нижче vin_min перетворювач не дотягне вихід,
// вище vin_max — ризик нагріву й виходу за гарантії.
bool input_within_spec(const power_spec_t *s, uint16_t vin_mv) {
    return vin_mv >= s->vin_min_mv && vin_mv <= s->vin_max_mv;
}

void power_up(void) {
    uint16_t vin = adc_read_vin_mv();
    if (!input_within_spec(&logic_5v, vin)) {
        log_warn("вхід %u мВ поза ТЗ [%u..%u] — старт заборонено",
                 vin, logic_5v.vin_min_mv, logic_5v.vin_max_mv);
        enter_safe_state();
        return;
    }
    enable_converter();
}
