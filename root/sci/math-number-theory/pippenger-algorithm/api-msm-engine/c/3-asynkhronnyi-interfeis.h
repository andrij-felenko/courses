/* Дескриптор асинхронної черги обчислень */
typedef struct msm_async_queue msm_async_queue_t;

/* Дескриптор асинхронного завдання */
typedef struct msm_task_handle msm_task_handle_t;

/**
 * Створення черги асинхронних завдань MSM.
 * @param num_workers Кількість фонових робочих потоків.
 * @return Вказівник на створену чергу або NULL у разі помилки.
 */
msm_async_queue_t* msm_async_queue_create(uint32_t num_workers);

/**
 * Відправка завдання MSM у неблокуючу чергу обчислень.
 */
msm_task_handle_t* msm_async_submit(
    msm_async_queue_t *queue,
    msm_point_jacobian_t *result,
    const msm_point_affine_t *points,
    const msm_fe256_t *scalars,
    size_t n,
    const msm_config_t *config
);

/**
 * Очікування завершення асинхронного завдання (блокуючий виклик).
 */
msm_status_t msm_async_wait(msm_task_handle_t *task);

/**
 * Неблокуюча перевірка готовності завдання.
 * @return true, якщо обчислення завершено.
 */
bool msm_async_poll(msm_task_handle_t *task);

/**
 * Знищення черги завдань та вивільнення ресурсів.
 */
void msm_async_queue_destroy(msm_async_queue_t *queue);
