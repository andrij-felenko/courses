/* Виклик у main() нової прошивки після проходження самоперевірок */
void app_main(void)
{
    /* 1. Ініціалізація периферії та живлення */
    hardware_early_init();
    watchdog_feed();

    /* 2. Перевірка внутрішніх вузлів (POST) */
    bool sensors_ok = sensors_self_test();
    bool comms_ok   = network_stack_connect();

    if (sensors_ok && comms_ok) {
        /* Всі критичні підсистеми працюють -> фіксуємо успіх у метаданих */
        bootloader_mark_image_confirmed();
    } else {
        /* Аварія підсистеми: не підтверджуємо слот, дозволяємо Watchdog скинути чіп */
        log_error("Self-test failed, waiting for watchdog rollback...");
        while (1) {
            /* Очікування перезапуску та відкату завантажувачем */
        }
    }

    /* 3. Перехід до основного робочого циклу */
    while (1) {
        watchdog_feed();
        process_telemetry();
    }
}
