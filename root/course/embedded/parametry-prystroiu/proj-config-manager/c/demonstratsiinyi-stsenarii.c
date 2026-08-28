int main(void) {
    printf("=== СТАРТ ТЕСТУВАННЯ ВІДМОВОСТІЙКОГО МЕНЕДЖЕРА КОНФІГУРАЦІЇ ===\n");
    cfg_manager_init();

    /* Спроба 1: Спроба надіслати некоректну конфігурацію (помилка реляційних меж) */
    cfg_payload_v2_t bad_candidate = g_active_config;
    bad_candidate.conn_timeout_s = 10;
    bad_candidate.report_interval_s = 60; /* Помилка: conn_timeout <= report_interval */

    printf("\n--- ТЕСТ 1: Відхилення некоректних залежностей ---\n");
    cfg_start_trial(&bad_candidate);

    /* Спроба 2: Коректний синтаксис, але сервер недосяжний (емуляція втрати зв'язку) */
    cfg_payload_v2_t unreachable_candidate = g_active_config;
    strncpy(unreachable_candidate.broker_host, "broken-server.invalid", sizeof(unreachable_candidate.broker_host) - 1);
    unreachable_candidate.conn_timeout_s = 180;
    unreachable_candidate.report_interval_s = 30;

    printf("\n--- ТЕСТ 2: Випробування кандидата та таймаутний відкат ---\n");
    if (cfg_start_trial(&unreachable_candidate)) {
        printf("Імітація 60 секунд відсутності мережевого handshake...\n");
        for (int sec = 0; sec < 60; ++sec) {
            cfg_timer_tick_1hz();
        }
    }

    /* Спроба 3: Успішне підключення та фіксація */
    cfg_payload_v2_t good_candidate = g_active_config;
    strncpy(good_candidate.broker_host, "prod-mqtt.domain.com", sizeof(good_candidate.broker_host) - 1);
    good_candidate.broker_port = 8883;

    printf("\n--- ТЕСТ 3: Успішний Trial Run та Commit ---\n");
    if (cfg_start_trial(&good_candidate)) {
        printf("Мережевий handshake успішний! Виклик confirm_commit()...\n");
        cfg_confirm_commit();
    }

    printf("\n=== ТЕСТУВАННЯ ЗАВЕРШЕНО УСПІШНО ===\n");
    return 0;
}
