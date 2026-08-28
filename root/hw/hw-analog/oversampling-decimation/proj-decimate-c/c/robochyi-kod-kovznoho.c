// Ковзний фільтр + проріджування = повний дециматор зі зниженням частоти.
static sliding_t g_flt;
static uint16_t  g_decim_cnt = 0;

void adc_isr(void) {
    uint16_t raw = adc_read_raw();
    uint16_t smoothed = sliding_push(&g_flt, raw);   // згладили (фільтр стоїть ПЕРЕД проріджуванням)

    if (++g_decim_cnt >= WIN) {                        // проріджуємо ÷WIN
        g_decim_cnt = 0;
        publish_sample(smoothed);                     // віддаємо лише кожен WIN-тий
    }
}
