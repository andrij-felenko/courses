/* ПРАВИЛЬНО: беззнакова дельта працює крізь будь-яку кількість переповнень */
void wait_for_event_safe(uint32_t timeout_ms) {
    uint32_t start = HAL_GetTick();
    
    while (!is_event_ready()) {
        if ((uint32_t)(HAL_GetTick() - start) >= timeout_ms) {
            handle_timeout();
            break;
        }
    }
}
