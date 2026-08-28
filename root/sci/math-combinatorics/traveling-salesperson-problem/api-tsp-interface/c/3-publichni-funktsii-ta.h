#ifdef __cplusplus
extern "C" {
#endif

/**
 * @brief Ініціалізація структури конфігурації за замовчуванням.
 * @param config Вказівник на структуру конфігурації.
 */
void tsp_config_init(tsp_config_t* config);

/**
 * @brief Головна функція розв'язання задачі комівояжера за матрицею відстаней.
 * @param matrix Матриця відстаней розміру n x n (одномірний масив row-major).
 * @param n Кількість вершин/міст у графі.
 * @param config Налаштування солвера (якщо NULL, використовуються за замовчуванням).
 * @param result Вихідна структура результату.
 * @return TSP_SUCCESS у разі успіху або код помилки.
 */
tsp_status_t tsp_solve_matrix(const double* matrix, size_t n, 
                             const tsp_config_t* config, 
                             tsp_result_t* result);

/**
 * @brief Звільнення динамічної пам'яті, виділеної у структурі результату.
 * @param result Вказівник на структуру результату.
 */
void tsp_result_free(tsp_result_t* result);

/**
 * @brief Перевірка матриці відстаней на відповідність нерівності трикутника.
 * @param matrix Матриця розміру n x n.
 * @param n Кількість вершин.
 * @return true — якщо нерівність трикутника виконується для всіх трійок вершин.
 */
bool tsp_validate_triangle_inequality(const double* matrix, size_t n);

#ifdef __cplusplus
}
#endif
