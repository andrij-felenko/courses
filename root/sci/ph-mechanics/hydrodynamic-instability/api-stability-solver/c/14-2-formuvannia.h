/**
 * @brief Обчислює повний спектр власних значень рівняння Орра — Зоммерфельда
 * 
 * Процедура виконує такі кроки:
 * 1. Збирає диф-матриці Чебишова D1, D2, D4 розміром (N+1) x (N+1).
 * 2. Формує комплексну матрицю лівого оператора A = (U - c)*(D2 - a²*I) - U''*I + i/(a*Re)*(D4 - 2a²D2 + a⁴I).
 * 3. Накладає граничні умови шляхом редукції рядків для стінок y = ±1.
 * 4. Викликає LAPACK zggev для знаходження комплексних власних чисел c.
 * 5. Впорядковує моди за зменшенням уявної частини c_i.
 * 
 * @param profile Валідний профіль швидкості U(y)
 * @param config Специфікація сітки та числа Рейнольдса
 * @param result[out] Структура з результатами обчислення спектра
 * @return HYDRO_SUCCESS у разі успішної збіжності алгоритму
 */
hydro_status_t hydro_solve_spectrum_orr_sommerfeld(
    const void *profile,
    const hydro_grid_config_t *config,
    hydro_spectrum_result_t *result
);

/**
 * @brief Обчислює спектр нестійкості Релея — Бенара для конвекції Буссінеска
 * 
 * @param config Специфікація сітки (N, Ra, Pr, alpha)
 * @param result[out] Структура з результатами обчислення
 * @return HYDRO_SUCCESS або код помилки
 */
hydro_status_t hydro_solve_spectrum_boussinesq(
    const hydro_grid_config_t *config,
    hydro_spectrum_result_t *result
);

/**
 * @brief Витягує амплітудну власну функцію ϕ(y) для заданої моди
 * @param result Валідний результат обчислення спектра
 * @param mode_idx Індекс моди (0 <= mode_idx < result->num_modes)
 * @param mode_shape_out[out] Виділений користувачем масив розміром N для збереження ϕ(y)
 * @return HYDRO_SUCCESS або HYDRO_ERR_INVALID_PARAM
 */
hydro_status_t hydro_get_mode_shape(
    const hydro_spectrum_result_t *result,
    int mode_idx,
    hydro_complex_t *mode_shape_out
);

/**
 * @brief Обчислює оптимальний резольвентний коефіцієнт підсилення G(omega)
 * 
 * @param profile Вказівник на профіль
 * @param config Конфігурація сітки
 * @param omega Частота вимушуючої сили omega
 * @param max_gain[out] Вихідне максимальне сингулярне значення резольвенти G(omega)
 * @return HYDRO_SUCCESS або код помилки
 */
hydro_status_t hydro_compute_resolvent_gain(
    const void *profile,
    const hydro_grid_config_t *config,
    double omega,
    double *max_gain
);

/**
 * @brief Обчислює максимальний перехідний ріст енергії G(t) немодального аналізу
 * 
 * @param profile Вказівник на профіль
 * @param config Конфігурація сітки
 * @param t Часовий момент t > 0
 * @param max_growth[out] Вихідне значення максимального коефіцієнта підсилення G(t)
 * @return HYDRO_SUCCESS або код помилки
 */
hydro_status_t hydro_compute_transient_growth(
    const void *profile,
    const hydro_grid_config_t *config,
    double t,
    double *max_growth
);

/**
 * @brief Налаштовує рівень логування діагностичних повідомлень
 * @param level Рівень логування
 */
void hydro_set_log_level(hydro_log_level_t level);

/**
 * @brief Повертає текстовий опис останньої помилки у даному потоці
 * @return Текстовий рядок опису помилки (статичний буфер)
 */
const char* hydro_get_last_error_message(void);

/**
 * @brief Звільняє пам'ять у структурі результатів спектрального розв'язання
 * @param result Вказівник на структуру результату
 */
void hydro_spectrum_result_free(hydro_spectrum_result_t *result);
