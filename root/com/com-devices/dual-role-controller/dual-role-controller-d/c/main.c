typedef enum { DIR_OFF, DIR_SOURCE, DIR_SINK } vbus_dir_t;

// Обидва ключі — пари back-to-back; кожен вивід кермує своєю парою.
static void set_vbus_direction(vbus_dir_t dir) {
    // 1) БЕЗУМОВНО закрити обидва напрями
    gpio_clear(GATE_SOURCE);      // ключ-джерело off
    gpio_clear(GATE_SINK);        // ключ-стік off

    // 2) мертвий час: дочекатись, поки обидва канали справді закрилися
    delay_us(DEADTIME_US);        // > часу вимикання ключа (типово десятки мкс)

    // 3) аж тепер увімкнути рівно один бік
    switch (dir) {
        case DIR_SOURCE: soft_start(GATE_SOURCE); break;  // плавно, проти inrush
        case DIR_SINK:   gpio_set(GATE_SINK);     break;
        case DIR_OFF:    /* лишаємось знеструмленими */   break;
    }
}
