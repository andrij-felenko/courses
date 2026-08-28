// Калібрування «нуля» при старті: усереднити кілька відліків тиші.
static int16_t zero_level = ADC_MIDSCALE;

void calibrate_zero(void) {
    int32_t acc = 0;
    for (int i = 0; i < 256; i++) acc += adc_read();
    zero_level = (int16_t)(acc / 256);    // реальна середина для ЦЬОГО екземпляра
}

int16_t read_signal(void) {
    return (int16_t)adc_read() - zero_level;
}
