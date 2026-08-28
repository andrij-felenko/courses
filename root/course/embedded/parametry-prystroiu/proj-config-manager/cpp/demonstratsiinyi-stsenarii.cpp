int main() {
    std::cout << "=== СТАРТ ТЕСТУВАННЯ ВІДМОВОСТІЙКОГО МЕНЕДЖЕРА (C++20) ===\n";
    embedded::config::FaultTolerantConfigManager manager;
    auto init_res = manager.initialize();
    if (!init_res) {
        std::cerr << "Помилка ініціалізації!\n";
        return 1;
    }

    // Тест 1: Невалідна конфігурація
    auto bad_candidate = manager.active_config();
    bad_candidate.conn_timeout_s = 10;
    bad_candidate.report_interval_s = 60;
    auto trial1 = manager.start_trial(bad_candidate);
    std::cout << "Тест 1 (Очікується помилка): " << (!trial1 ? "ВІДХИЛЕНО УСПІШНО" : "ЗБІЙ ТЕСТУ") << "\n";

    // Тест 2: Випробування з таймаутом і відкатом
    auto unreachable_candidate = manager.active_config();
    std::strncpy(unreachable_candidate.broker_host, "bad.host", sizeof(unreachable_candidate.broker_host) - 1);
    unreachable_candidate.conn_timeout_s = 180;
    unreachable_candidate.report_interval_s = 30;

    if (manager.start_trial(unreachable_candidate)) {
        std::cout << "Тест 2: Прокручування 60 секунд таймера...\n";
        for (int i = 0; i < 60; ++i) {
            manager.tick_1hz();
        }
        std::cout << "Тест 2 стан після таймауту: "
                  << (!manager.is_trial_active() ? "ВІДКАТ ВИКОНАНО" : "ПОМИЛКА") << "\n";
    }

    // Тест 3: Успішний commit
    auto good_candidate = manager.active_config();
    std::strncpy(good_candidate.broker_host, "prod.broker.io", sizeof(good_candidate.broker_host) - 1);
    if (manager.start_trial(good_candidate)) {
        auto commit_res = manager.confirm_commit();
        std::cout << "Тест 3 (Фіксація): " << (commit_res ? "УСПІХ" : "ЗБІЙ") << "\n";
        std::cout << "Поточний активний брокер: " << manager.active_config().broker_host << "\n";
    }

    return 0;
}
