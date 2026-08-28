// Глобальний стан дециматора та прапорець «готово».
static volatile block_dec_t g_dec = {0, 0};
static volatile uint16_t    g_result;
static volatile bool        g_ready = false;

// Обробник переривання таймера АЦП: викликається на кожен сирий відлік.
void IRAM_ATTR adc_isr(void) {
    uint16_t raw = adc_read_raw();         // швидке читання регістра АЦП
    uint16_t out;
    if (block_push((block_dec_t *)&g_dec, raw, &out)) {
        g_result = out;                    // блок готовий
        g_ready  = true;                   // сигналимо основному циклу
    }
}

void loop(void) {
    if (g_ready) {
        g_ready = false;
        uint16_t value14 = g_result;       // 14-бітне число, 0..16380
        // ... вжити value14: відправити, показати, порівняти з порогом ...
    }
}
