#define PULSE_CH   ADC_CHANNEL_6     // вихід S давача — на канал АЦП1
#define SAMPLE_US  20000             // період опитування: 20 мс = 50 Гц

static int64_t g_lastSample = 0;

static void pulse_task(void *arg) {
    while (1) {
        int64_t now = esp_timer_get_time();      // мікросекунди від старту
        if (now - g_lastSample >= SAMPLE_US) {
            g_lastSample += SAMPLE_US;           // НЕ '= now' — так період не «повзе»
            int raw = 0;
            adc_oneshot_read(s_adc, PULSE_CH, &raw);
            process(raw);                        // уся обробка — тут
        }
        vTaskDelay(1);                           // віддати такт іншим задачам
    }
}
