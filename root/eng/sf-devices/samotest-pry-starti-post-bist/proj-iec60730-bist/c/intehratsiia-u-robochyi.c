void safety_periodic_tick(void) {
    bool flash_done = false;

    /* 1. Тестуємо чергові 64 байти ОЗП */
    bist_status_t st = bist_slice_ram_march_c(&g_ram_ctx);
    if (st != BIST_OK) {
        bist_enter_safe_state(st);
    }

    /* 2. Рахуємо черговий 1 КБ Flash */
    st = bist_slice_flash_crc32(&g_flash_ctx, &flash_done);
    if (st != BIST_OK) {
        bist_enter_safe_state(st);
    }

    /* 3. Годуємо Watchdog ТІЛЬКИ якщо всі BIST-слайси пройшли успішно */
    watchdog_feed();
}
