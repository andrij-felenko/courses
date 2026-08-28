/**
 * @brief Обчислює поглинання для масиву частот (спектральний аналіз).
 * 
 * @param[in]  env  Вказівник на структуру параметрів середовища.
 * @param[in]  frequencies_hz  Масив частот у Гц.
 * @param[in]  count  Кількість частот у масиві.
 * @param[out] out_alpha_db_km  Масив для збереження коефіцієнтів у дБ/км.
 * @return iso9613_status_t Статус виконання.
 */
iso9613_status_t iso9613_calculate_spectrum(
    const iso9613_environment_t *env,
    const double *frequencies_hz,
    size_t count,
    double *out_alpha_db_km
);
