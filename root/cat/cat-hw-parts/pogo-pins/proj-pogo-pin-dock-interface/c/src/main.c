/**
 * @file main.c
 * @brief Демонстрація роботи монітора Pogo Pin з імітацією вібраційних збурень.
 */

#include "pogo_pin_monitor.h"
#include <stdio.h>

int main(void) {
    printf("Запуск системи аналізу вібростійкості пружинних контактів Pogo Pin...\n");

    pogo_config_t config = {
        .min_glitch_duration_us = 10,   // Фіксуємо розриви довші за 10 мкс
        .debounce_filter_us = 2,
        .sampling_period_ms = 100
    };

    pogo_monitor_t monitor;
    pogo_monitor_init(&monitor, &config);

    // Імітація випробування на вібростенді тривалістю 1000 мс (1 секунда)
    uint32_t t_us = 1000;

    // Нормальний притиснутий контакт
    pogo_monitor_handle_edge(&monitor, true, t_us);

    // Симуляція першого короткого відскоку плунжера через вібрацію (тривалість 25 мкс)
    t_us += 50000;
    pogo_monitor_handle_edge(&monitor, false, t_us); // розімкнення
    t_us += 25;
    pogo_monitor_handle_edge(&monitor, true, t_us);  // відновлення контакту

    // Симуляція другого мікророзриву (тривалість 80 мкс)
    t_us += 120000;
    pogo_monitor_handle_edge(&monitor, false, t_us);
    t_us += 80;
    pogo_monitor_handle_edge(&monitor, true, t_us);

    // Симуляція високочастотного шуму менше порогу (3 мкс) - має бути проігнорований
    t_us += 200000;
    pogo_monitor_handle_edge(&monitor, false, t_us);
    t_us += 3;
    pogo_monitor_handle_edge(&monitor, true, t_us);

    // Симуляція третього значного розриву (тривалість 150 мкс)
    t_us += 300000;
    pogo_monitor_handle_edge(&monitor, false, t_us);
    t_us += 150;
    pogo_monitor_handle_edge(&monitor, true, t_us);

    // Завершення тесту тривалістю 1000 мс
    pogo_monitor_update_stats(&monitor, 1000);
    pogo_monitor_print_report(&monitor);

    return 0;
}
