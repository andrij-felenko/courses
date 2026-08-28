#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <stdint.h>

// Статус виконання окремого кроку обчислення
typedef enum {
    TASK_RUNNING,
    TASK_HALTED,
    TASK_FAILED
} TaskStatus;

// Структура завдання (покроковий автомат)
typedef struct Task {
    uint32_t task_id;
    uint32_t current_state;
    uint64_t accumulated_steps;
    int32_t result_value;
    bool completed;
} Task;

// Контекст планувальника Dovetailing
typedef struct DovetailScheduler {
    Task *tasks;
    size_t task_capacity;
    size_t task_count;
    int32_t *results;
    size_t result_capacity;
    size_t result_count;
} DovetailScheduler;

// Симуляція одного кроку обчислень для задачі id
static TaskStatus step_task(Task *task) {
    if (task->completed) {
        return TASK_HALTED;
    }

    task->accumulated_steps++;

    // Приклад моделювання обчислення генератора
    task->current_state = (task->current_state * 1103515245 + 12345) & 0x7FFFFFFF;

    if ((task->current_state + task->task_id) % 17 == 0) {
        task->result_value = (int32_t)(task->accumulated_steps * 10 + task->task_id);
        task->completed = true;
        return TASK_HALTED;
    }

    return TASK_RUNNING;
}

DovetailScheduler* scheduler_create(size_t initial_capacity) {
    DovetailScheduler *sched = (DovetailScheduler*)malloc(sizeof(DovetailScheduler));
    if (!sched) return NULL;

    sched->task_capacity = initial_capacity;
    sched->task_count = 0;
    sched->tasks = (Task*)malloc(sizeof(Task) * initial_capacity);

    sched->result_capacity = initial_capacity;
    sched->result_count = 0;
    sched->results = (int32_t*)malloc(sizeof(int32_t) * initial_capacity);

    if (!sched->tasks || !sched->results) {
        free(sched->tasks);
        free(sched->results);
        free(sched);
        return NULL;
    }
    return sched;
}

void scheduler_add_task(DovetailScheduler *sched, uint32_t task_id) {
    if (sched->task_count >= sched->task_capacity) {
        sched->task_capacity *= 2;
        sched->tasks = (Task*)realloc(sched->tasks, sizeof(Task) * sched->task_capacity);
    }
    Task *t = &sched->tasks[sched->task_count++];
    t->task_id = task_id;
    t->current_state = task_id + 1;
    t->accumulated_steps = 0;
    t->result_value = 0;
    t->completed = false;
}

static void add_result(DovetailScheduler *sched, int32_t val) {
    for (size_t i = 0; i < sched->result_count; ++i) {
        if (sched->results[i] == val) return;
    }
    if (sched->result_count >= sched->result_capacity) {
        sched->result_capacity *= 2;
        sched->results = (int32_t*)realloc(sched->results, sizeof(int32_t) * sched->result_capacity);
    }
    sched->results[sched->result_count++] = val;
    printf("[ENUMERATOR C] Знайдено елемент RE-множини: %d\n", val);
}

// Запуск обходу сітки за діагоналями s = 1..max_diagonals
void scheduler_run_dovetailing(DovetailScheduler *sched, size_t max_diagonals) {
    for (size_t s = 1; s <= max_diagonals; ++s) {
        for (size_t i = 0; i < s && i < sched->task_count; ++i) {
            Task *t = &sched->tasks[i];
            if (t->completed) continue;

            TaskStatus status = step_task(t);
            if (status == TASK_HALTED) {
                add_result(sched, t->result_value);
            }
        }
    }
}

void scheduler_free(DovetailScheduler *sched) {
    if (!sched) return;
    free(sched->tasks);
    free(sched->results);
    free(sched);
}
