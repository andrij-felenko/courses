// НЕКОРЕКТНО: Використання календарного часу для затримок і таймаутів
void process_sensor_bad() {
    static uint64_t next_run_wall = get_wall_clock_ms();
    uint64_t current_wall = get_wall_clock_ms();

    // При стрибку wall-clock назад next_run_wall виявиться в майбутньому!
    if (current_wall >= next_run_wall) {
        read_sensor();
        next_run_wall = current_wall + 1000; // Пауза 1 секунда
    }
}

// КОРЕКТНО: Використання монотонного uptime для планування інтервалів
void process_sensor_good() {
    static uint64_t next_run_up = get_monotonic_uptime_ms();
    uint64_t current_up = get_monotonic_uptime_ms();

    // Uptime зростає монотонно, стрибки календарного часу не впливають на цикл
    if (current_up >= next_run_up) {
        read_sensor();
        next_run_up = current_up + 1000; // Гарантований інтервал 1000 мс
    }
}
