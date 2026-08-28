#include <stddef.h>
#include <stdbool.h>

/**
 * @brief Сигнатура зворотного виклику прогресу виконання C-API.
 * @param completed_tasks Кількість завершених точок.
 * @param total_tasks Загальна кількість точок сітки.
 * @param user_data Користувацький вказівник контексту.
 * @return true продовжує обчислення, false перериває процес.
 */
typedef bool (*circle_map_progress_cb_t)(
    size_t completed_tasks,
    size_t total_tasks,
    void *user_data
);
