while (1) {
    status_t res = sensor_read_all();
    if (res != STATUS_OK) {
        // Помилка шини: пропускаємо розрахунок, але продовжуємо цикл
        wdt_refresh();
        continue;
    }
    control_step();
    wdt_refresh();
}
