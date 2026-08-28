// Модель у прошивці: оцінити, скільки хвилин з'їдає доданий вантаж-обчислювач.
// Вхід: ємність батареї, базова потужність апарата, потужність обчислювача.
float flight_time_min(float E_wh, float P_base_w, float P_compute_w) {
    float P_total = P_base_w + P_compute_w;   // повна потужність
    return (E_wh / P_total) * 60.0f;          // Вт·год / Вт = год → у хвилини
}

// Малий апарат: батарея 40 Вт·год, база 100 Вт (мотори + FC)
float t0    = flight_time_min(40.0f, 100.0f, 0.0f);    // 24.0 хв  (без обчислювача)
float t_rpi = flight_time_min(40.0f, 100.0f, 10.0f);   // 21.8 хв  (+Raspberry Pi-клас, ~10 Вт)
float t_jet = flight_time_min(40.0f, 100.0f, 25.0f);   // 19.2 хв  (+Jetson на повній, ~25 Вт)
