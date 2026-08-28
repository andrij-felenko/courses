/* КАТАСТРОФІЧНА ПОМИЛКА: пряме додавання дедлайну ламається при переповненні */
void wait_for_event_broken(uint32_t timeout_ms) {
    uint32_t deadline = HAL_GetTick() + timeout_ms;
    
    while (!is_event_ready()) {
        if (HAL_GetTick() >= deadline) {
            handle_timeout();
            break;
        }
    }
}
