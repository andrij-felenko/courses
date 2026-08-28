/* ПРАВИЛЬНО: різниця (now - start) дає точний інтервал у кільцевій групі 2³² */
void wait_for_event_safe(uint32_t timeout_ms) {
    const uint32_t start = SystemTick::get_tick();

    while (!is_event_ready()) {
        if ((SystemTick::get_tick() - start) >= timeout_ms) {
            handle_timeout();
            break;
        }
    }
}
