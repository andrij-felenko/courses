// Без volatile компілятор має право закешувати значення в регістрі
uint32_t g_counter = 0;

void IRAM_ATTR timer_isr(void *arg) {
    g_counter++;                     // переривання збільшує лічильник
}

void app_main(void) {
    esp_timer_start_periodic(timer, 100);  // переривання кожні 100 мкс

    while (1) {
        if (g_counter >= 1000) {
            do_something();
            g_counter = 0;
        }
        // Без друку компілятор кешує g_counter у регістрі —
        // цикл ніколи не бачить оновлень із переривання → завис
    }
}
