/**
 * @brief Створює новий екземпляр вихорової системи
 * 
 * @param config Позитивна конфігурація розв'язувача
 * @param init_points Початковий масив вихорових точок розміром config->num_vortices
 * @param system_handle[out] Вихідний вказівник на створений об'єкт
 * @return VORTEX_SUCCESS або код помилки
 */
vortex_status_t vortex_system_create(
    const vortex_solver_config_t *config,
    const vortex_point_t *init_points,
    void **system_handle
);

/**
 * @brief Виконує один крок часового інтегрування системи вихорів
 * 
 * @param system_handle Валідний об'єкт системи
 * @return VORTEX_SUCCESS або VORTEX_ERR_INTEGRATION_DIVERGED
 */
vortex_status_t vortex_system_step(void *system_handle);

/**
 * @brief Обчислює індуковану швидкість потоку у довільній точці простору (x, y, z)
 * 
 * @param system_handle Вказівник на систему
 * @param px Координата точки X
 * @param py Координата точки Y
 * @param pz Координата точки Z
 * @param vx[out] Індукована швидкість V_x
 * @param vy[out] Індукована швидкість V_y
 * @param vz[out] Індукована швидкість V_z
 * @return VORTEX_SUCCESS або VORTEX_ERR_INVALID_PARAM
 */
vortex_status_t vortex_compute_induced_velocity(
    const void *system_handle,
    double px, double py, double pz,
    double *vx, double *vy, double *vz
);

/**
 * @brief Обчислює поточні значення інваріантів руху (циркуляція, момент, енергія)
 * 
 * @param system_handle Вказівник на систему
 * @param invariants[out] Вихідна структура інваріантів
 * @return VORTEX_SUCCESS або VORTEX_ERR_INVALID_PARAM
 */
vortex_status_t vortex_system_get_invariants(
    const void *system_handle,
    vortex_invariants_t *invariants
);

/**
 * @brief Звільняє пам'ять вихорової системи
 * @param system_handle Вказівник на систему
 */
void vortex_system_free(void *system_handle);
