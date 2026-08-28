/**
 * @brief Створює профіль швидкості плоскопаралельного потоку Поазейля U(y) = 1 - y²
 * 
 * Обчислює дійсні значення швидкості U(y) та її другої похідної U''(y) = -2 у точках Чебишова.
 * 
 * @param config Позитивна конфігурація сітки (N, Re, alpha)
 * @param profile[out] Подвійний вказівник на створену структуру профілю
 * @return HYDRO_SUCCESS або код помилки HYDRO_ERR_INVALID_PARAM / HYDRO_ERR_OUT_OF_MEMORY
 */
hydro_status_t hydro_profile_create_poiseuille(
    const hydro_grid_config_t *config,
    void **profile
);

/**
 * @brief Створює профіль швидкості вільного зсувного шару U(y) = tanh(y)
 * 
 * Обчислює U(y) = tanh(y) та другу похідну U''(y) = -2*tanh(y)*(1 - tanh²(y)) у точках Чебишова.
 * 
 * @param config Позитивна конфігурація сітки
 * @param profile[out] Подвійний вказівник на створену структуру профілю
 * @return HYDRO_SUCCESS або код помилки
 */
hydro_status_t hydro_profile_create_tanh(
    const hydro_grid_config_t *config,
    void **profile
);

/**
 * @brief Створює пограничний шар Блазіуса U(η) за розв'язком рівняння Блазіуса
 * 
 * @param config Конфігурація сітки
 * @param profile[out] Подвійний вказівник на вихідну структуру
 * @return HYDRO_SUCCESS або код помилки
 */
hydro_status_t hydro_profile_create_blasius(
    const hydro_grid_config_t *config,
    void **profile
);

/**
 * @brief Створює початковий шар нестійкості Рихтмаєра — Мешкова
 * 
 * @param config Конфігурація сітки (atwood, delta_v)
 * @param profile[out] Вказівник на створений профіль
 * @return HYDRO_SUCCESS або код помилки
 */
hydro_status_t hydro_profile_create_shock_interface(
    const hydro_grid_config_t *config,
    void **profile
);

/**
 * @brief Перераховує 3D параметри збурення в 2D за теоремою Сквайрса
 * 
 * @param alpha 3D подовжнє хвильове число
 * @param beta 3D поперечне хвильове число
 * @param re 3D число Рейнольдса
 * @param alpha_2d[out] Еквівалентне 2D хвильове число
 * @param re_2d[out] Еквівалентне 2D число Рейнольдса
 */
void hydro_transform_squire_3d_to_2d(
    double alpha,
    double beta,
    double re,
    double *alpha_2d,
    double *re_2d
);

/**
 * @brief Створює користувальницький профіль швидкості за вказаними масивами U(y) та U''(y)
 * 
 * @param config Конфігурація сітки
 * @param u_values Масив значень швидкості розміром N+1
 * @param u_pp_values Масив значень другої похідної швидкості розміром N+1
 * @param profile[out] Подвійний вказівник на вихідну структуру
 * @return HYDRO_SUCCESS або код помилки
 */
hydro_status_t hydro_profile_create_custom(
    const hydro_grid_config_t *config,
    const double *u_values,
    const double *u_pp_values,
    void **profile
);

/**
 * @brief Звільняє пам'ять, виділену під профіль швидкості
 * @param profile Вказівник на профіль
 */
void hydro_profile_free(void *profile);
