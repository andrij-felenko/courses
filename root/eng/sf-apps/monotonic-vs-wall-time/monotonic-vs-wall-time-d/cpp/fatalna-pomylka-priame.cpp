/* КАТАСТРОФІЧНА ПОМИЛКА: розрахунок абсолютної точки на 32-бітному таймері */
void wait_for_event_broken(uint32_t timeout_ms) {
    uint32_t deadline = SystemTick::get_tick() + timeout_ms;

    while (!is_event_ready()) {
        if (SystemTick::get_tick() >= deadline) {
            handle_timeout();
            break;
        }
    }
}
