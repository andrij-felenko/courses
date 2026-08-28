// ── flicker.c ── та сама логіка; вибірку рівномірно жене задача FreeRTOS,
// а годинник — esp_timer (мікросекунди). Пороги в 12-бітних одиницях.
typedef struct {
    adc_oneshot_unit_handle_t adc;
    adc_channel_t ch;
    float    lo, hi;          // смуга «вогняних» частот, Гц
    float    mean, hyst;      // повільне середнє й зона нечутливості
    bool     prev_above;
    uint16_t crossings;
    int64_t  win_start;       // мкс
    float    last_freq;
} flicker_t;

static void flicker_begin(flicker_t *f) {
    int v = 0;
    adc_oneshot_read(f->adc, f->ch, &v);
    f->mean = (float)v;       // старт середнього — з поточного рівня
    f->hyst = 32.0f;          // 12 біт замість 10 → зона нечутливості вчетверо ширша
    f->prev_above = false;
    f->crossings  = 0;
    f->win_start  = esp_timer_get_time();
    f->last_freq  = 0.0f;
}

// Кликати з задачі рівним кроком ~5 мс (200 Гц вибірки).
static void flicker_sample(flicker_t *f) {
    int v = 0;
    if (adc_oneshot_read(f->adc, f->ch, &v) != ESP_OK) return;

    const float alpha = 0.02f;            // «важке» середнє: йде за рівнем, не за пульсом
    f->mean += alpha * ((float)v - f->mean);

    // Перетин знизу вгору з гістерезисом — той самий тригер Шмітта в коді.
    if (!f->prev_above && v > f->mean + f->hyst) { f->crossings++; f->prev_above = true; }
    else if (f->prev_above && v < f->mean - f->hyst) f->prev_above = false;

    int64_t now = esp_timer_get_time();
    int64_t dt  = now - f->win_start;
    if (dt >= 1000000) {                  // вікно 1 с, час у мікросекундах
        f->last_freq = (f->crossings * 1000000.0f) / (float)dt;
        f->crossings = 0;
        f->win_start = now;
    }
}

static bool  flicker_flame(const flicker_t *f) { return f->last_freq >= f->lo && f->last_freq <= f->hi; }
static int   flicker_level(const flicker_t *f) { return (int)f->mean; }
