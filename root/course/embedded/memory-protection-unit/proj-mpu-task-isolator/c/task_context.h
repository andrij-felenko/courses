#ifndef TASK_CONTEXT_H
#define TASK_CONTEXT_H

#include "mpu_types.h"
#include "mpu_isolator.h"

#ifdef __cplusplus
extern "C" {
#endif

/* Тип функції входу задачі */
typedef void (*task_entry_fn)(void *arg);

/* Дескриптор задачі з ізоляцією пам'яті */
typedef struct {
    uint32_t                  task_id;
    uint32_t                 *stack_top;        /* Поточний показник стека PSP */
    mpu_task_isolation_desc_t isolation_desc;
    bool                      is_privileged;
    bool                      is_active;
    const char               *task_name;
} task_control_block_t;

/**
 * @brief Ініціалізація початкового стек-фрейму задачі для непривілейованого старту.
 * @param tcb Вказівник на блок керування задачею.
 * @param entry Точка входу в функцію задачі.
 * @param arg Аргумент, що передається у задачу.
 * @param stack_buffer Масив пам'яті під стек.
 * @param stack_size_bytes Розмір стека.
 * @param guard_size_bytes Розмір захисної смуги під стеком.
 */
void task_create_context(task_control_block_t *tcb,
                         task_entry_fn         entry,
                         void                 *arg,
                         uint32_t             *stack_buffer,
                         uint32_t              stack_size_bytes,
                         uint32_t              guard_size_bytes,
                         const char           *name);

/**
 * @brief Перехід у непривілейований режим потоку (Thread Mode with Unprivileged Access).
 */
void task_drop_privileges(void);

/**
 * @brief Програмний системний виклик SVC для безпечного звернення до служб ядра.
 * @param svc_number Номер системної служби.
 * @param param1 Перший параметр виклику.
 * @param param2 Другий параметр виклику.
 * @return Результат виконання системної служби.
 */
uint32_t task_syscall(uint32_t svc_number, uint32_t param1, uint32_t param2);

#ifdef __cplusplus
}
#endif

#endif /* TASK_CONTEXT_H */
