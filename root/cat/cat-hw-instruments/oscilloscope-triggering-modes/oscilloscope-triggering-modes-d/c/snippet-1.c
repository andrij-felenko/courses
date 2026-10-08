// Логіка роботи циклу тригеризації в режимі Auto
while (oscilloscope_is_running) {
    reset_watchdog_timer();
    bool event_detected = false;
    
    // Очікування події компаратора до вичерпання таймауту
    while (read_watchdog_timer_ms() < AUTO_TIMEOUT_MS) {
        if (check_comparator_hardware_flag()) {
            start_horizontal_sweep(SWEEP_MODE_SYNCHRONIZED);
            event_detected = true;
            break;
        }
    }
    
    // Якщо компаратор мовчить — примусове оновлення екрана
    if (!event_detected) {
        start_horizontal_sweep(SWEEP_MODE_FORCED);
    }
    
    wait_sweep_and_retrace_completion();
}
