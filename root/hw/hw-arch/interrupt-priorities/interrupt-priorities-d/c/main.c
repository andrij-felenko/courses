volatile uint32_t g_ticks = 0;     // лічильник таймера
volatile bool     g_pressed = false;

// Високий рівень (3): короткий, лиш інкремент — він перебиватиме GPIO
static void IRAM_ATTR timer_isr(void *arg) {
    g_ticks++;                     // ← одна дія, кілька тактів
}

// Низький рівень (1): довший обробник кнопки
static void IRAM_ATTR gpio_isr(void *arg) {
    g_pressed = true;
    for (int i = 0; i < 50; i++)   // ← навмисно затягнутий: тут його й перебʼє таймер
        debounce_step();
}

void app_main(void) {
    intr_handle_t ht, hg;
    esp_intr_alloc(ETS_TG0_T0_LEVEL_INTR_SOURCE,
                   ESP_INTR_FLAG_LEVEL3 | ESP_INTR_FLAG_IRAM,   // рівень 3 — вищий
                   timer_isr, NULL, &ht);
    esp_intr_alloc(ETS_GPIO_INTR_SOURCE,
                   ESP_INTR_FLAG_LEVEL1 | ESP_INTR_FLAG_IRAM,   // рівень 1 — нижчий
                   gpio_isr, NULL, &hg);
}
