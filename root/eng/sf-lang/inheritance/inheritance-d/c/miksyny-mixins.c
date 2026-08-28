#include <stdio.h>

/* В C міксини імітують через таблиці функціональних покажчиків та агрегацію */
typedef struct {
    void (*log_start)(void);
    void (*log_end)(void);
} LoggerOps;

static void default_start(void) { printf("[LOG] Початок виконання операції\n"); }
static void default_end(void)   { printf("[LOG] Операцію завершено\n"); }

static const LoggerOps g_default_logger = { default_start, default_end };

typedef struct {
    const LoggerOps* logger;
    int task_id;
} TaskWithLogging;

void task_execute(TaskWithLogging* self) {
    self->logger->log_start();
    printf("Виконуються корисні обчислення для завдання %d...\n", self->task_id);
    self->logger->log_end();
}

int main(void) {
    TaskWithLogging task = { &g_default_logger, 101 };
    task_execute(&task);
    return 0;
}
