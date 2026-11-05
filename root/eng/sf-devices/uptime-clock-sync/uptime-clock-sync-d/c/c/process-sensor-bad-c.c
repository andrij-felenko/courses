// НЕКОРЕКТНО: Залежність виконання циклу від wall-clock часу
void process_sensor_bad_c(void) {
    static uint64_t next_run_wall = 0;
    uint64_t current_wall = get_wall_clock_ms();

    if (next_run_wall == 0) {
        next_run_wall = current_wall + 1000;
    }

    if (current_wall >= next_run_wall) {
        read_sensor();
        next_run_wall = current_wall + 1000;
    }
}

// КОРЕКТНО: Розрахунок інтервалу через різницю монотонних тиків
void process_sensor_good_c(void) {
    static uint64_t last_run_up = 0;
    uint64_t current_up = get_monotonic_uptime_ms();

    // Обчислення різниці захищає від переповнення та не залежить від NTP
    if (current_up - last_run_up >= 1000) {
        read_sensor();
        last_run_up = current_up;
    }
}
