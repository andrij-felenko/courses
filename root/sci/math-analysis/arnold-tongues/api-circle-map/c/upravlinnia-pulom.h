typedef struct circle_map_thread_pool circle_map_thread_pool_t;

/**
 * @brief Створює новий пул обчислювальних потоків.
 */
circle_map_thread_pool_t* circle_map_thread_pool_create(size_t num_threads);

/**
 * @brief Знищує пул потоків та вивільняє ресурси.
 */
void circle_map_thread_pool_destroy(circle_map_thread_pool_t *pool);
