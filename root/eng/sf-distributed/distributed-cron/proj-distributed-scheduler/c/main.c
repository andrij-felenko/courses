#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <time.h>

#define WHEEL_SLOTS 60
#define WHEEL_TICK_SEC 1
#define MAX_NAME_LEN 64

/* Структура періодичної задачі */
typedef struct cron_task {
    uint64_t job_id;
    char name[MAX_NAME_LEN];
    uint64_t interval_sec;
    uint64_t next_run_utc;
    uint32_t remaining_rounds;
    struct cron_task* next;
} cron_task_t;

/* Часове колесо для одного шарду */
typedef struct {
    cron_task_t* slots[WHEEL_SLOTS];
    uint32_t current_slot;
    uint64_t current_time_sec;
} timing_wheel_t;

/* Контекст лізи та огорожі шарду */
typedef struct {
    uint32_t shard_id;
    uint64_t fencing_epoch;
    uint64_t lease_deadline_utc;
    bool is_active;
} shard_lease_t;

/* Стан воркера для перевірки огорожі */
typedef struct {
    uint64_t highest_seen_epoch;
} worker_fencing_state_t;

/* Ініціалізація часового колеса */
void wheel_init(timing_wheel_t* w, uint64_t start_time) {
    memset(w->slots, 0, sizeof(w->slots));
    w->current_slot = 0;
    w->current_time_sec = start_time;
}

/* Додавання задачі у часове колесо: O(1) */
void wheel_add_task(timing_wheel_t* w, cron_task_t* task) {
    int64_t delay = (int64_t)(task->next_run_utc - w->current_time_sec);
    if (delay < 0) delay = 0;

    uint64_t ticks = (uint64_t)delay / WHEEL_TICK_SEC;
    task->remaining_rounds = (uint32_t)(ticks / WHEEL_SLOTS);
    uint32_t target_slot = (uint32_t)((w->current_slot + ticks) % WHEEL_SLOTS);

    task->next = w->slots[target_slot];
    w->slots[target_slot] = task;
}

/* Диспатч задачі воркеру з токеном огорожі */
void dispatch_to_worker(const cron_task_t* task, uint64_t epoch, worker_fencing_state_t* worker) {
    printf("[DISPATCH] Запуск задачі ID=%llu ('%s'), Слот=%llu UTC, Епоха=%llu\n",
           (unsigned long long)task->job_id, task->name,
           (unsigned long long)task->next_run_utc, (unsigned long long)epoch);

    /* Перевірка огорожі на боці воркера/сховища */
    if (epoch < worker->highest_seen_epoch) {
        printf("  [ВОРКЕР: ВІДХИЛЕНО] Запізнілий сигнал зомбі-планувальника! (Епоха %llu < %llu)\n",
               (unsigned long long)epoch, (unsigned long long)worker->highest_seen_epoch);
        return;
    }

    worker->highest_seen_epoch = epoch;
    printf("  [ВОРКЕР: ПРИЙНЯТО] Успішне виконання бізнес-логіки для епохи %llu.\n",
           (unsigned long long)epoch);
}

/* Просування часу на один такт (1 секунда): O(1) */
void wheel_tick(timing_wheel_t* w, shard_lease_t* lease, worker_fencing_state_t* worker) {
    w->current_time_sec += WHEEL_TICK_SEC;
    w->current_slot = (w->current_slot + 1) % WHEEL_SLOTS;

    /* Перевірка чинності лізи володіння шардом */
    if (!lease->is_active || w->current_time_sec > lease->lease_deadline_utc) {
        printf("[WARN] Ліза шарду %u спливла! Зупинка генерації тригерів.\n", lease->shard_id);
        return;
    }

    cron_task_t** curr = &w->slots[w->current_slot];
    while (*curr != NULL) {
        cron_task_t* task = *curr;
        if (task->remaining_rounds > 0) {
            task->remaining_rounds--;
            curr = &task->next;
        } else {
            /* Виймаємо задачу зі списку поточного слота */
            *curr = task->next;
            task->next = NULL;

            /* Відправляємо тригер на виконання */
            dispatch_to_worker(task, lease->fencing_epoch, worker);

            /* Перераховуємо наступний запуск для періодичної задачі */
            task->next_run_utc = w->current_time_sec + task->interval_sec;
            wheel_add_task(w, task);
        }
    }
}

int main(void) {
    uint64_t now = 1700000000;
    timing_wheel_t wheel;
    wheel_init(&wheel, now);

    shard_lease_t lease = {
        .shard_id = 1,
        .fencing_epoch = 100,
        .lease_deadline_utc = now + 10,
        .is_active = true
    };

    worker_fencing_state_t worker = { .highest_seen_epoch = 0 };

    /* Реєструємо дві періодичні задачі */
    cron_task_t task1 = {
        .job_id = 101,
        .name = "Database Backup",
        .interval_sec = 2,
        .next_run_utc = now + 2,
        .remaining_rounds = 0,
        .next = NULL
    };
    cron_task_t task2 = {
        .job_id = 102,
        .name = "Billing Settlement",
        .interval_sec = 5,
        .next_run_utc = now + 5,
        .remaining_rounds = 0,
        .next = NULL
    };

    wheel_add_task(&wheel, &task1);
    wheel_add_task(&wheel, &task2);

    printf("=== СТАРТ СИМУЛЯЦІЇ ПЛАНУВАЛЬНИКА (Епоха 100) ===\n");
    for (int sec = 1; sec <= 6; sec++) {
        printf("\n--- Час: T + %d с ---\n", sec);
        wheel_tick(&wheel, &lease, &worker);
    }

    printf("\n=== СИМУЛЯЦІЯ ПАУЗИ ТА ЗМІНИ ЛІДЕРА (Нова Епоха 101) ===\n");
    /* Новий лідер зафіксував свіжішу епоху у воркері */
    worker.highest_seen_epoch = 101;

    /* Старий планувальник виходить із паузи і намагається виконати тригер зі старою епохою 100 */
    printf("Старий вузол із зомбі-епохою 100 надсилає запізнілий тригер:\n");
    dispatch_to_worker(&task1, lease.fencing_epoch, &worker);

    return 0;
}
