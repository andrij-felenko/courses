/* Головний цикл обробки подій із централізованим диспетчером сну (C) */
void main_loop(void) {
    while (1) {
        /* 1. Обробка всіх накопичених подій у черзі */
        event_t ev;
        while (event_queue_pop(&ev)) {
            dispatch_event(&ev);
        }

        /* 2. Якщо черга порожня — оцінка допустимої глибини сну */
        uint32_t next_deadline_ms = timer_get_ms_to_next_deadline();
        pm_sleep_if_idle(next_deadline_ms);
    }
}
