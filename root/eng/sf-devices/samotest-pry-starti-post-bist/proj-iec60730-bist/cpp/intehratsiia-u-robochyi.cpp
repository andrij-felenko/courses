void safety_periodic_tick() noexcept {
    // 1. Тестуємо чергові 64 байти ОЗП
    if (const auto st = g_ram_scanner.scan_next_slice(); st != safety::Status::Ok) {
        safety::enter_safe_state(st);
    }

    // 2. Рахуємо черговий 1 КБ Flash
    if (const auto [st, finished] = g_flash_scanner.scan_quantum(); st != safety::Status::Ok) {
        safety::enter_safe_state(st);
    }

    // 3. Годуємо Watchdog ТІЛЬКИ якщо всі BIST-слайси пройшли успішно
    watchdog_feed();
}
