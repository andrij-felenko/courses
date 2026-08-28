/**
 * @brief Обчислює атмосферне поглинання для заданої частоти та параметрів середовища.
 * 
 * @param[in]  env  Вказівник на структуру параметрів середовища.
 * @param[in]  frequency_hz  Частота акустичної хвилі у Гц.
 * @param[out] result  Вказівник на структуру для запису результатів.
 * @return iso9613_status_t Статус виконання (ISO9613_SUCCESS у разі успіху).
 */
iso9613_status_t iso9613_calculate_attenuation(
    const iso9613_environment_t *env,
    double frequency_hz,
    iso9613_attenuation_result_t *result
);
