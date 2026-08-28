#include <stdint.h>
#include <stdbool.h>

typedef void (*task_callback_t)(uint32_t current_time_us);

typedef struct {
    task_callback_t run;
    uint32_t period_us;
    uint32_t next_run_us;
    uint8_t priority;
} task_entry_t;

#define NUM_TASKS 3

static void task_attitude_pid(uint32_t now) {
    /* Розрахунок стабілізації (тривалість 35 мкс) */
}

static void task_telemetry_mavlink(uint32_t now) {
    /* Передача телеметрії (тривалість 25 мкс) */
}

static void task_battery_monitor(uint32_t now) {
    /* Зчитування АЦП напруги батареї (тривалість 10 мкс) */
}

static task_entry_t task_table[NUM_TASKS] = {
    { task_attitude_pid,      1000, 0, 10 }, /* 1 кГц, пріоритет 10 */
    { task_telemetry_mavlink, 20000, 0, 5 },  /* 50 Гц, пріоритет 5  */
    { task_battery_monitor,  100000, 0, 1 }   /* 10 Гц, пріоритет 1  */
};

void run_cooperative_scheduler(void) {
    uint32_t now = get_system_micros();
    int8_t best_task = -1;
    uint8_t highest_priority = 0;

    /* Вибір найбільш пріоритетної готової задачі */
    for (uint8_t i = 0; i < NUM_TASKS; ++i) {
        if ((int32_t)(now - task_table[i].next_run_us) >= 0) {
            if (best_task == -1 || task_table[i].priority > highest_priority) {
                best_task = i;
                highest_priority = task_table[i].priority;
            }
        }
    }

    if (best_task >= 0) {
        task_entry_t *t = &task_table[best_task];
        t->run(now);
        t->next_run_us += t->period_us;
    }
}
