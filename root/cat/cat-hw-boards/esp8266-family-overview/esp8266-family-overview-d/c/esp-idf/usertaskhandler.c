// Приклад кооперативної задачі в Non-OS SDK з використанням системної черги
#include "ets_sys.h"
#include "osapi.h"
#include "user_interface.h"

#define USER_TASK_PRIO 0
#define USER_TASK_QUEUE_LEN 4
static os_event_t userTaskQueue[USER_TASK_QUEUE_LEN];

static void userTaskHandler(os_event_t *e) {
    // Обробка події без блокування головного потоку
    if (e->sig == 1) {
        // Виконання атомарного кроку обчислень
        doSingleStep(e->par);
        // Скидання програмного вартового таймера
        system_soft_wdt_feed();
    }
}

void initUserTask(void) {
    // Реєстрація системної задачі у кооперативному планувальнику Non-OS SDK
    system_os_task(userTaskHandler, USER_TASK_PRIO, userTaskQueue, USER_TASK_QUEUE_LEN);
}
