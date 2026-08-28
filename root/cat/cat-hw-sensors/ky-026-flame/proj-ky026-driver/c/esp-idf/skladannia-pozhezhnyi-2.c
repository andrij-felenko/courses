static adc_oneshot_unit_handle_t adc;   // ADC1 — блок, дружній до Wi-Fi
static float ir_l = 0, ir_r = 0;        // згладжена сила жару зліва / справа

static void read_sensors(void) {
    const float a = 0.15f;              // згладжування: гасить тремтіння полумʼя
    int l = 0, r = 0;
    adc_oneshot_read(adc, AO_L_CH, &l);
    adc_oneshot_read(adc, AO_R_CH, &r);
    ir_l += a * ((float)l - ir_l);
    ir_r += a * ((float)r - ir_r);
}
