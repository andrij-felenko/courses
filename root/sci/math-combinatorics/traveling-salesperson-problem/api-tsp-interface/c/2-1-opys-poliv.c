/**
 * @brief Функція зворотного виклику для відстеження прогресу (Callback).
 * @param progress Дробове значення від 0.0 (початок) до 1.0 (завершення).
 * @param user_data Вказівник на контекст користувача.
 * @return true — продовжувати обчислення, false — негайно перервати обчислення.
 */
typedef bool (*tsp_progress_cb)(double progress, void* user_data);

/**
 * @brief Конфігураційна структура параметрів солвера.
 */
typedef struct {
    tsp_algorithm_t algorithm;  /* Обраний алгоритм розв'язання */
    tsp_metric_type_t metric;   /* Тип метрики вхідних даних */
    double time_limit_sec;      /* Ліміт часу в секундах (0.0 — без обмеження) */
    double target_precision;    /* Бажаний коефіцієнт точності (наприклад 0.05 = 5%) */
    size_t num_threads;         /* Кількість паралельних потоків обробки */
    tsp_progress_cb callback;   /* Функція зворотного виклику для прогресу */
    void* user_data;            /* Контекстний вказівник для колбеку */
} tsp_config_t;

/**
 * @brief Структура для повернення результату розв'язання.
 */
typedef struct {
    tsp_status_t status;        /* Код статусу виконання */
    double tour_cost;           /* Загальна довжина/вага знайденого маршруту */
    int* tour;                  /* Динамічний масив послідовності вершин розміру (n + 1) */
    size_t tour_size;           /* Кількість елементів у масиві tour (n + 1) */
    double elapsed_time_sec;    /* Фактично витрачений час обчислення у секундах */
    uint64_t nodes_evaluated;   /* Кількість переглянутих станів/вузлів дерева */
} tsp_result_t;
