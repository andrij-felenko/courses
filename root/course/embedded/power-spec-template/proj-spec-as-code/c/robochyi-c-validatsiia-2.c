void power_up_checked(void) {
    int viol = validate_against_spec(&logic_5v, &parts_5v);
    if (viol) {
        printf("СТАРТ ЗАБОРОНЕНО: %d порушень ТЗ обраними деталями\n", viol);
        enter_safe_state();
        return;
    }
    // далі — звичайна перевірка реального входу проти вікна ТЗ (зі статті)
    uint16_t vin = adc_read_vin_mv();
    if (vin < logic_5v.vin_min_mv || vin > logic_5v.vin_max_mv) {
        printf("вхід %u мВ поза ТЗ — старт заборонено\n", vin);
        enter_safe_state();
        return;
    }
    enable_converter();
}
