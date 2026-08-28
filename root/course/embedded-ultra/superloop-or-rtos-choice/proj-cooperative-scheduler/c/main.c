#include <stdint.h>
#include <stdbool.h>

#define SCHEDULER_MAX_TASKS 8

typedef void (*task_fn_t)(uint32_t current_time_us);

typedef enum {
    TASK_PRIORITY_LOW    = 0,
    TASK_PRIORITY_MEDIUM = 1,
    TASK_PRIORITY_HIGH   = 2,
    TASK_PRIORITY_REALTIME = 3
} task_priority_t;

typedef struct {
    task_fn_t callback;
    uint32_t period_us;
    uint32_t next_execution_us;
    uint32_t max_exec_time_us;
    uint32_t total_exec_time_us;
    uint32_t execution_count;
    task_priority_t priority;
    volatile uint8_t event_flags;
    bool enabled;
} task_descriptor_t;

typedef struct {
    task_descriptor_t tasks[SCHEDULER_MAX_TASKS];
    uint8_t task_count;
    uint32_t total_overruns;
    uint32_t cpu_load_permille; /* Завантаження CPU у проміле (0.1%) */
} scheduler_t;

/* Системна функція отримання монотонного часу в мікросекундах */
extern uint32_t platform_micros(void);

/* Переведення процесора в режим низького енергоспоживання до переривання */
extern void platform_sleep_wfi(void);

void scheduler_init(scheduler_t *sched) {
    sched->task_count = 0;
    sched->total_overruns = 0;
    sched->cpu_load_permille = 0;
    for (uint8_t i = 0; i < SCHEDULER_MAX_TASKS; ++i) {
        sched->tasks[i].enabled = false;
        sched->tasks[i].event_flags = 0;
    }
}

bool scheduler_add_task(scheduler_t *sched, task_fn_t fn, uint32_t period_us, task_priority_t priority) {
    if (sched->task_count >= SCHEDULER_MAX_TASKS || fn == NULL) {
        return false;
    }

    uint8_t idx = sched->task_count++;
    uint32_t now = platform_micros();

    sched->tasks[idx].callback = fn;
    sched->tasks[idx].period_us = period_us;
    sched->tasks[idx].next_execution_us = now + period_us;
    sched->tasks[idx].max_exec_time_us = 0;
    sched->tasks[idx].total_exec_time_us = 0;
    sched->tasks[idx].execution_count = 0;
    sched->tasks[idx].priority = priority;
    sched->tasks[idx].event_flags = 0;
    sched->tasks[idx].enabled = true;

    return true;
}

void scheduler_trigger_event(scheduler_t *sched, uint8_t task_id, uint8_t flag) {
    if (task_id < sched->task_count) {
        sched->tasks[task_id].event_flags |= flag;
    }
}

void scheduler_dispatch(scheduler_t *sched) {
    uint32_t now = platform_micros();
    int16_t selected_task_idx = -1;
    task_priority_t highest_priority = TASK_PRIORITY_LOW;
    int32_t max_time_overdue = 0;
    bool is_event_triggered = false;

    /* Пошук найбільш пріоритетної готової задачі */
    for (uint8_t i = 0; i < sched->task_count; ++i) {
        task_descriptor_t *t = &sched->tasks[i];
        if (!t->enabled) continue;

        /* Перевірка наявності асинхронної події від ISR */
        if (t->event_flags != 0) {
            selected_task_idx = i;
            highest_priority = t->priority;
            is_event_triggered = true;
            break;
        }

        int32_t delta = (int32_t)(now - t->next_execution_us);
        if (delta >= 0) {
            if (selected_task_idx == -1 || t->priority > highest_priority ||
               (t->priority == highest_priority && delta > max_time_overdue)) {
                selected_task_idx = i;
                highest_priority = t->priority;
                max_time_overdue = delta;
            }
        }
    }

    if (selected_task_idx != -1) {
        task_descriptor_t *task = &sched->tasks[selected_task_idx];
        uint32_t start_us = platform_micros();

        if (is_event_triggered) {
            task->event_flags = 0; /* Очищення прапорців події */
        }

        /* Виклик тіла задачі */
        task->callback(start_us);

        uint32_t exec_duration = platform_micros() - start_us;
        task->total_exec_time_us += exec_duration;
        task->execution_count++;
        if (exec_duration > task->max_exec_time_us) {
            task->max_exec_time_us = exec_duration;
        }

        /* Оновлення сітки часу для періодичних задач */
        if (task->period_us > 0) {
            task->next_execution_us += task->period_us;

            /* Детекція катастрофічного перевантаження */
            now = platform_micros();
            if ((int32_t)(now - task->next_execution_us) >= (int32_t)task->period_us) {
                sched->total_overruns++;
                task->next_execution_us = now + task->period_us;
            }
        }
    } else {
        /* Якщо жодна задача не готова, переводимо ядро в режим низького струму */
        platform_sleep_wfi();
    }
}
