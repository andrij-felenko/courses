// Спробувати оживити панель до `tries` разів. Кожна спроба — повне скидання + таблиця.
disp_status_t st7789_start_safe(int tries) {
    for (int t = 0; t < tries; t++) {
        hw_reset();                                   // чистий аркуш щоразу
        disp_status_t st = run_init_table_checked(
            st7789_table,
            sizeof(st7789_table) / sizeof(st7789_table[0]));
        if (st == DISP_OK) {
            return DISP_OK;                           // ожила — виходимо
        }
        // не вдалося — даємо залізу видихнути й заходимо знову
        delay_ms(50);
    }
    return DISP_ERR_BUS;                              // усі спроби марні — хай вирішує вище
}
