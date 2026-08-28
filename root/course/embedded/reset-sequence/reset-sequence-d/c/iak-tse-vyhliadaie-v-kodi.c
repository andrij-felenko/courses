// Безпечне згортання перед будь-яким перезапуском на ESP32.
// Викликається автоматично з esp_restart() — у порядку, зворотному до реєстрації.

static void on_shutdown(void)
{
    // 1) Виходи — у безпечний стан, поки ще керуємо залізом.
    //    Найтерміновіше: некерований мотор/нагрів небезпечний.
    motors_all_stop();
    heater_off();
    valve_set_safe();

    // 2) Зберегти критичний стан у нелетку памʼять і ДОЧЕКАТИСЬ запису.
    nvs_save_critical_state();      // лічильники, незбережені виміри
    nvs_commit_blocking();          // не йдемо далі, поки не лягло у флеш

    // 3) Ввічливо згорнути звʼязок: інша сторона побачить чисте завершення.
    net_close_all_sockets();

    // 4) Лишити слід для майбутньої діагностики.
    reboot_counter_increment();     // викриє цикл перезавантажень
    log_reset_reason(g_reset_why);  // «оновлення», «зміна конфігу», «soft-fault»...
}

void app_init(void)
{
    esp_register_shutdown_handler(on_shutdown);
    // ... звичайний старт ...
}

// Десь у логіці: вирішили перезавантажитись (нове налаштування / OTA / soft-fault)
void request_graceful_reset(reset_reason_t why)
{
    g_reset_why = why;
    esp_restart();   // спершу відпрацює on_shutdown(), тоді — власне reset
}
