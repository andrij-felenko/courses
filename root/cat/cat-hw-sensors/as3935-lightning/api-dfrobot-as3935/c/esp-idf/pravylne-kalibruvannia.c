// Порахувати частоту LCO для заданої ємності tune (0..15).
// Повертає виміряну частоту в Гц (уже помножену на дільник).
static uint32_t measure_lco(uint8_t tune) {
    uint8_t r;
    as3935_read(0x08, &r);
    as3935_write(0x08, (r & 0xF0) | (tune & 0x0F));   // TUN_CAP: 0, 8, 16 … 120 пФ
    as3935_read(0x08, &r);
    as3935_write(0x08, r | 0x80);                     // DISP_LCO=1 → LCO на пін IRQ
    vTaskDelay(pdMS_TO_TICKS(2));                     // дати сигналу устоятися

    // Рахуємо фронти на піні IRQ за вікно 100 мс.
    const int64_t window_us = 100000;
    uint32_t edges = 0;
    int last = gpio_get_level(IRQ_GPIO);
    int64_t t0 = esp_timer_get_time();
    while (esp_timer_get_time() - t0 < window_us) {
        int now = gpio_get_level(IRQ_GPIO);
        if (now == 1 && last == 0) edges++;           // порахувати фронт ↑
        last = now;
    }
    as3935_read(0x08, &r);
    as3935_write(0x08, r & ~0xE0);                    // ПРИБРАТИ гетеродин з піна!

    // edges за 0.1 с → ·10, щоб дістати за секунду; дільник LCO_FDIV = 16
    return edges * 10U * 16U;
}

// Перебрати 16 ємностей, знайти ту, де частота найближча до 500 кГц.
static uint8_t find_best_caps(void) {
    const int32_t target = 500000;                    // 500 кГц
    uint8_t best = 0;
    int32_t best_err = INT32_MAX;
    for (uint8_t tune = 0; tune < 16; tune++) {
        int32_t f = (int32_t)measure_lco(tune);
        int32_t err = f > target ? f - target : target - f;   // |f − 500 кГц|
        ESP_LOGI(TAG, "tune=%u  f=%ld  промах=%ld", tune, (long)f, (long)err);
        if (err < best_err) { best_err = err; best = tune; }
    }
    ESP_LOGI(TAG, "Найкраща ємність: tune=%u (%u пФ)", best, best * 8);
    return best;
}
